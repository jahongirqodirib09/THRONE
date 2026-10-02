from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from config import GAME_TITLE, MAX_PLAYERS, MIN_PLAYERS
from database import add_group, add_or_update_player
from game_engine import GameEngine
from game_state import GamePhase, PlayerState


# Har bir guruh uchun alohida o‘yin.
GAMES: dict[int, GameEngine] = {}


def get_game(chat_id: int) -> GameEngine:
    """Guruhning o‘yin obyektini qaytaradi."""

    if chat_id not in GAMES:
        GAMES[chat_id] = GameEngine(chat_id)

    return GAMES[chat_id]


def lobby_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """Lobby tugmalari."""

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "👑 O‘yinga qo‘shilish",
                    callback_data=f"join:{chat_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🚪 O‘yindan chiqish",
                    callback_data=f"leave:{chat_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🎮 O‘yinni boshlash",
                    callback_data=f"start:{chat_id}",
                ),
            ],
        ]
    )


def voting_keyboard(
    chat_id: int,
    game: GameEngine,
) -> InlineKeyboardMarkup:
    """Tirik o‘yinchilar uchun ovoz berish tugmalari."""

    buttons: list[list[InlineKeyboardButton]] = []

    for player in game.state.alive_players():
        buttons.append(
            [
                InlineKeyboardButton(
                    f"⚔️ {player_display_name(player)}",
                    callback_data=(
                        f"vote:{chat_id}:{player.user_id}"
                    ),
                )
            ]
        )

    return InlineKeyboardMarkup(buttons)


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Telegram /start komandasi."""

    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if user is None or chat is None or message is None:
        return

    await add_or_update_player(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name or "",
    )

    # Shaxsiy chat.
    if chat.type == "private":
        await message.reply_text(
            f"👑 {GAME_TITLE}\n\n"
            "Assalomu alaykum!\n\n"
            "⚔️ THRONE — Taxtlar O‘yini.\n\n"
            "Botni guruhga qo‘shing va guruhda /start "
            "komandasini bering."
        )
        return

    # Guruhni bazaga yozish.
    await add_group(
        chat_id=chat.id,
        title=chat.title,
    )

    game = get_game(chat.id)

    if game.state.phase != GamePhase.LOBBY:
        await message.reply_text(
            "⚔️ Bu guruhda hozir o‘yin davom etmoqda."
        )
        return

    # /start bergan odamni avtomatik lobbyga qo‘shamiz.
    game.add_player(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name or "",
    )

    await message.reply_text(
        build_lobby_text(game),
        reply_markup=lobby_keyboard(chat.id),
    )


async def join_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """O‘yinga qo‘shilish tugmasi."""

    query = update.callback_query

    if query is None or query.from_user is None:
        return

    chat_id = parse_chat_id(query.data)

    if chat_id is None:
        await query.answer(
            "⚠️ Tugma ma'lumoti noto‘g‘ri.",
            show_alert=True,
        )
        return

    game = get_game(chat_id)

    if game.state.phase != GamePhase.LOBBY:
        await query.answer(
            "⚠️ O‘yin allaqachon boshlangan.",
            show_alert=True,
        )
        return

    if game.state.player_count() >= MAX_PLAYERS:
        await query.answer(
            "⚠️ O‘yinchilar soni to‘ldi.",
            show_alert=True,
        )
        return

    user = query.from_user

    added = game.add_player(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name or "",
    )

    if not added:
        await query.answer(
            "Siz allaqachon o‘yindasiz.",
            show_alert=True,
        )
        return

    await add_or_update_player(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name or "",
    )

    await query.answer("👑 Siz o‘yinga qo‘shildingiz.")

    await update_lobby_message(query, game)


async def leave_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """O‘yindan chiqish tugmasi."""

    query = update.callback_query

    if query is None or query.from_user is None:
        return

    chat_id = parse_chat_id(query.data)

    if chat_id is None:
        await query.answer(
            "⚠️ Tugma ma'lumoti noto‘g‘ri.",
            show_alert=True,
        )
        return

    game = get_game(chat_id)

    if game.state.phase != GamePhase.LOBBY:
        await query.answer(
            "⚠️ O‘yin boshlangan. Endi chiqib bo‘lmaydi.",
            show_alert=True,
        )
        return

    removed = game.remove_player(query.from_user.id)

    if not removed:
        await query.answer(
            "Siz lobbida emassiz.",
            show_alert=True,
        )
        return

    await query.answer("🚪 O‘yindan chiqdingiz.")

    await update_lobby_message(query, game)


async def start_game_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Admin o‘yinni boshlaydi."""

    query = update.callback_query

    if query is None or query.from_user is None:
        return

    chat_id = parse_chat_id(query.data)

    if chat_id is None:
        await query.answer(
            "⚠️ Tugma ma'lumoti noto‘g‘ri.",
            show_alert=True,
        )
        return

    if query.message is None:
        await query.answer(
            "⚠️ Xabar topilmadi.",
            show_alert=True,
        )
        return

    if query.message.chat.type not in (
        "group",
        "supergroup",
    ):
        await query.answer(
            "⚠️ Bu tugma faqat guruhda ishlaydi.",
            show_alert=True,
        )
        return

    # Adminni tekshirish.
    try:
        member = await context.bot.get_chat_member(
            chat_id=chat_id,
            user_id=query.from_user.id,
        )
    except Exception:
        await query.answer(
            "⚠️ Adminlikni tekshirib bo‘lmadi.",
            show_alert=True,
        )
        return

    if member.status not in (
        "administrator",
        "creator",
    ):
        await query.answer(
            "⚠️ O‘yinni faqat guruh administratori "
            "boshlashi mumkin.",
            show_alert=True,
        )
        return

    game = get_game(chat_id)

    if not game.can_start():
        await query.answer(
            f"Kamida {MIN_PLAYERS} o‘yinchi kerak.",
            show_alert=True,
        )
        return

    started = game.start_game()

    if not started:
        await query.answer(
            "⚠️ O‘yinni boshlashda xatolik yuz berdi.",
            show_alert=True,
        )
        return

    await query.answer("🎮 O‘yin boshlandi!")

    try:
        await query.edit_message_text(
            build_game_started_text(game)
        )
    except Exception:
        pass

    # Rollarni shaxsiy botga yuborish.
    await send_private_roles(
        context=context,
        game=game,
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=build_night_text(game),
    )


async def vote_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Test uchun ovoz berishni boshlaydi.

    Keyinchalik kun tugashi bilan avtomatik chaqiriladi.
    """

    chat = update.effective_chat
    message = update.effective_message

    if chat is None or message is None:
        return

    if chat.type not in ("group", "supergroup"):
        return

    game = get_game(chat.id)

    if game.state.phase != GamePhase.DAY:
        await message.reply_text(
            "⚠️ Hozir ovoz berish bosqichi emas."
        )
        return

    if not game.start_voting():
        await message.reply_text(
            "⚠️ Ovoz berishni boshlashda xatolik yuz berdi."
        )
        return

    await message.reply_text(
        "🗳️ OVOZ BERISH\n\n"
        "Kimni chiqarish kerak deb hisoblaysiz?\n"
        "Quyidagi tugmalardan birini tanlang.",
        reply_markup=voting_keyboard(
            chat.id,
            game,
        ),
    )


async def vote_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Ovoz berish tugmasi."""

    query = update.callback_query

    if query is None or query.from_user is None:
        return

    data = query.data or ""
    parts = data.split(":")

    if len(parts) != 3:
        await query.answer(
            "⚠️ Ovoz tugmasi noto‘g‘ri.",
            show_alert=True,
        )
        return

    try:
        chat_id = int(parts[1])
        target_id = int(parts[2])
    except ValueError:
        await query.answer(
            "⚠️ Ovoz ma'lumoti noto‘g‘ri.",
            show_alert=True,
        )
        return

    game = get_game(chat_id)

    if game.state.phase != GamePhase.VOTING:
        await query.answer(
            "⚠️ Hozir ovoz berish vaqti emas.",
            show_alert=True,
        )
        return

    success = game.vote(
        voter_id=query.from_user.id,
        target_id=target_id,
    )

    if not success:
        await query.answer(
            "⚠️ Ovoz berib bo‘lmaydi.",
            show_alert=True,
        )
        return

    await query.answer("✅ Ovoz qabul qilindi.")

    target_name = game.player_name(target_id)

    try:
        await query.edit_message_text(
            "🗳️ Ovoz qabul qilindi.\n\n"
            f"Tanlovingiz: ⚔️ {target_name}"
        )
    except Exception:
        pass


def build_lobby_text(game: GameEngine) -> str:
    """Lobby xabari."""

    players = game.state.joined_players()

    lines = [
        f"👑 {GAME_TITLE}",
        "",
        "🏰 O‘YIN LOBBISI",
        "",
        f"👥 O‘yinchilar: "
        f"{len(players)}/{MAX_PLAYERS}",
        f"🎯 Boshlash uchun: {MIN_PLAYERS} ta o‘yinchi",
        "",
    ]

    if players:
        lines.append("👤 Ishtirokchilar:")

        for number, player in enumerate(
            players,
            start=1,
        ):
            lines.append(
                f"{number}. {player_display_name(player)}"
            )
    else:
        lines.append(
            "Hozircha hech kim qo‘shilmagan."
        )

    lines.extend(
        [
            "",
            "⚔️ O‘yinni guruh administratori boshlaydi.",
        ]
    )

    return "\n".join(lines)


def build_game_started_text(
    game: GameEngine,
) -> str:
    """O‘yin boshlanganidagi guruh xabari."""

    return (
        f"👑 {GAME_TITLE}\n\n"
        "⚔️ O‘YIN BOSHLANDI!\n\n"
        f"👥 O‘yinchilar: "
        f"{game.state.player_count()}\n"
        "🌙 Hozirgi bosqich: TUN\n\n"
        "📩 Rollaringiz shaxsiy botga yuboriladi.\n"
        "🤫 Roliingizni boshqalarga aytmang."
    )


def build_night_text(game: GameEngine) -> str:
    """Tun xabari."""

    return (
        f"🌙 {GAME_TITLE}\n\n"
        "🌙 TUN BOSHLANDI\n\n"
        "🏰 Qirollik jimjitlikka cho‘mdi.\n"
        "Har bir rol o‘z vazifasini bajaradi.\n\n"
        "⏳ Tungi bosqich boshlandi."
    )


async def send_private_roles(
    context: ContextTypes.DEFAULT_TYPE,
    game: GameEngine,
) -> None:
    """Har bir o‘yinchiga rolini shaxsiy xabarda yuboradi."""

    for player in game.state.joined_players():
        role = game.get_role_info(player.user_id)

        if role is None:
            continue

        teammates = game.get_teammates(
            player.user_id
        )

        text = (
            f"👑 {GAME_TITLE}\n\n"
            "🎭 SIZNING ROLINGIZ\n\n"
            f"{role['name']}\n"
            f"🏰 Jamoa: {role['side']}\n\n"
            "📜 Vazifa:\n"
            f"{role['description']}\n"
        )

        if teammates:
            text += (
                "\n🤝 Sizning sheriklaringiz:\n"
            )

            for teammate in teammates:
                text += (
                    f"• {player_display_name(teammate)}\n"
                )

        try:
            await context.bot.send_message(
                chat_id=player.user_id,
                text=text,
            )
        except Exception:
            # Foydalanuvchi botni hali ochmagan bo‘lsa,
            # guruhdagi o‘yinni to‘xtatmaymiz.
            continue


async def update_lobby_message(
    query,
    game: GameEngine,
) -> None:
    """Lobby xabarini yangilaydi."""

    try:
        await query.edit_message_text(
            build_lobby_text(game),
            reply_markup=lobby_keyboard(
                game.state.chat_id
            ),
        )
    except Exception:
        pass


def player_display_name(
    player: PlayerState,
) -> str:
    """O‘yinchi nomini qaytaradi."""

    if player.first_name:
        return player.first_name

    if player.username:
        return f"@{player.username}"

    return str(player.user_id)


def parse_chat_id(
    data: str | None,
) -> int | None:
    """Callback ma'lumotidan chat IDni oladi."""

    if not data:
        return None

    parts = data.split(":")

    if len(parts) != 2:
        return None

    try:
        return int(parts[1])
    except ValueError:
        return None


def register_handlers(application) -> None:
    """Telegram handlerlarini ulaydi."""

    application.add_handler(
        CommandHandler(
            "start",
            start_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "vote",
            vote_command,
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            join_callback,
            pattern=r"^join:-?\d+$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            leave_callback,
            pattern=r"^leave:-?\d+$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            start_game_callback,
            pattern=r"^start:-?\d+$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            vote_callback,
            pattern=r"^vote:-?\d+:\d+$",
        )
)
