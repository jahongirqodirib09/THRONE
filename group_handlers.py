# ============================================================
# THRONE — GROUP HANDLERS
# ============================================================

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatType

from config import CREATOR_ID
from game_engine import (
    MIN_PLAYERS,
    MAX_PLAYERS,
    get_game,
    get_players,
    get_player_count,
    create_new_game,
    join_game,
    leave_game,
    start_game,
    stop_game,
    get_alive_game_players,
    check_victory,
)
from game_messages import (
    lobby_message,
    player_list_message,
    player_join_message,
    player_leave_message,
    game_start_message,
    night_message,
    morning_message,
    discussion_message,
    voting_message,
    last_words_message,
    elimination_message,
    game_stop_message,
    game_finish_message,
)
from keyboards import (
    game_lobby_keyboard,
    game_control_keyboard,
    voting_keyboard,
    last_words_keyboard,
)

router = Router(name="throne_group_handlers")


# ============================================================
# GROUP CHECK
# ============================================================

def is_group(message: Message) -> bool:
    return message.chat.type in {
        ChatType.GROUP,
        ChatType.SUPERGROUP,
    }


# ============================================================
# ADMIN CHECK
# ============================================================

async def is_admin(message: Message) -> bool:
    if not is_group(message):
        return False

    member = await message.bot.get_chat_member(
        message.chat.id,
        message.from_user.id,
    )

    return member.status in {
        "administrator",
        "creator",
    }


# ============================================================
# /NEWGAME
# ============================================================

@router.message(Command("newgame"))
async def new_game_handler(message: Message):

    if not is_group(message):
        await message.answer(
            "⚠️ THRONE o‘yinini faqat guruhda boshlash mumkin."
        )
        return

    if not await is_admin(message):
        await message.answer(
            "🔒 O‘yinni faqat guruh administratori yaratishi mumkin."
        )
        return

    chat_id = message.chat.id

    existing_game = await get_game(chat_id)

    if existing_game:
        status = existing_game.get("status")

        if status not in {
            "finished",
            "stopped",
        }:
            await message.answer(
                "⚠️ Bu guruhda allaqachon faol THRONE o‘yini mavjud."
            )
            return

    try:
        game = await create_new_game(
            chat_id=chat_id,
            creator_id=message.from_user.id,
        )
    except Exception:
        await message.answer(
            "❌ O‘yinni yaratishda xatolik yuz berdi."
        )
        return

    await message.answer(
        lobby_message(game),
        reply_markup=game_lobby_keyboard(
            can_start=False
        ),
    )


# ============================================================
# /JOIN
# ============================================================

@router.message(Command("join"))
async def join_command(message: Message):

    if not is_group(message):
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    game = await get_game(chat_id)

    if not game:
        await message.answer(
            "⚠️ Hozircha faol o‘yin yo‘q.\n\n"
            "/newgame orqali yangi o‘yin yarating."
        )
        return

    try:
        result = await join_game(
            chat_id=chat_id,
            user_id=user_id,
            username=message.from_user.username or "",
            first_name=message.from_user.first_name or "",
        )
    except Exception:
        result = False

    if not result:
        await message.answer(
            "❌ O‘yinga qo‘shilib bo‘lmadi.\n\n"
            "O‘yin boshlangan yoki o‘yinchilar soni limitga yetgan "
            "bo‘lishi mumkin."
        )
        return

    players = await get_players(chat_id)
    count = len(players)

    await message.answer(
        player_join_message(message.from_user.first_name),
        reply_markup=game_lobby_keyboard(
            can_start=count >= MIN_PLAYERS
        ),
    )


# ============================================================
# /LEAVE
# ============================================================

@router.message(Command("leave"))
async def leave_command(message: Message):

    if not is_group(message):
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    game = await get_game(chat_id)

    if not game:
        await message.answer(
            "⚠️ Faol o‘yin yo‘q."
        )
        return

    try:
        result = await leave_game(
            chat_id=chat_id,
            user_id=user_id,
        )
    except Exception:
        result = False

    if not result:
        await message.answer(
            "❌ Siz o‘yindan chiqa olmadingiz."
        )
        return

    await message.answer(
        player_leave_message(
            message.from_user.first_name
        )
    )


# ============================================================
# /START
# ============================================================

@router.message(Command("start"))
async def start_game_command(message: Message):

    if not is_group(message):
        return

    if not await is_admin(message):
        await message.answer(
            "🔒 O‘yinni faqat guruh administratori boshlashi mumkin."
        )
        return

    chat_id = message.chat.id

    game = await get_game(chat_id)

    if not game:
        await message.answer(
            "⚠️ Faol o‘yin mavjud emas.\n\n"
            "/newgame orqali o‘yin yarating."
        )
        return

    players = await get_players(chat_id)
    count = len(players)

    if count < MIN_PLAYERS:
        await message.answer(
            f"⚠️ O‘yinni boshlash uchun kamida "
            f"{MIN_PLAYERS} ta o‘yinchi kerak.\n\n"
            f"👥 Hozir: {count}"
        )
        return

    if count > MAX_PLAYERS:
        await message.answer(
            f"⚠️ O‘yinchilar soni {MAX_PLAYERS} tadan oshmasligi kerak."
        )
        return

    try:
        result = await start_game(
            chat_id=chat_id,
            admin_id=message.from_user.id,
        )
    except Exception:
        result = False

    if not result:
        await message.answer(
            "❌ O‘yinni boshlashning imkoni bo‘lmadi."
        )
        return

    await message.answer(
        game_start_message(),
        reply_markup=game_control_keyboard(),
    )

    await message.answer(
        night_message()
    )


# ============================================================
# /STOP
# ============================================================

@router.message(Command("stop"))
async def stop_game_command(message: Message):

    if not is_group(message):
        return

    if not await is_admin(message):
        await message.answer(
            "🔒 O‘yinni faqat guruh administratori to‘xtata oladi."
        )
        return

    chat_id = message.chat.id

    game = await get_game(chat_id)

    if not game:
        await message.answer(
            "⚠️ Faol o‘yin yo‘q."
        )
        return

    try:
        result = await stop_game(
            chat_id=chat_id,
            admin_id=message.from_user.id,
        )
    except Exception:
        result = False

    if not result:
        await message.answer(
            "❌ O‘yinni to‘xtatib bo‘lmadi."
        )
        return

    await message.answer(
        game_stop_message()
    )


# ============================================================
# CALLBACK — JOIN
# ============================================================

@router.callback_query(F.data == "game_join")
async def game_join_callback(
    callback: CallbackQuery,
):

    if callback.message is None:
        return

    if callback.message.chat.type not in {
        ChatType.GROUP,
        ChatType.SUPERGROUP,
    }:
        await callback.answer(
            "O‘yinga faqat guruhdan qo‘shilishingiz mumkin.",
            show_alert=True,
        )
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    game = await get_game(chat_id)

    if not game:
        await callback.answer(
            "Faol o‘yin mavjud emas.",
            show_alert=True,
        )
        return

    try:
        result = await join_game(
            chat_id=chat_id,
            user_id=user_id,
            username=callback.from_user.username or "",
            first_name=callback.from_user.first_name or "",
        )
    except Exception:
        result = False

    if not result:
        await callback.answer(
            "O‘yinga qo‘shilib bo‘lmadi.",
            show_alert=True,
        )
        return

    players = await get_players(chat_id)

    await callback.answer(
        "👑 Siz THRONE o‘yiniga qo‘shildingiz!"
    )

    await callback.message.edit_reply_markup(
        reply_markup=game_lobby_keyboard(
            can_start=len(players) >= MIN_PLAYERS
        )
    )


# ============================================================
# CALLBACK — LEAVE
# ============================================================

@router.callback_query(F.data == "game_leave")
async def game_leave_callback(
    callback: CallbackQuery,
):

    if callback.message is None:
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    result = await leave_game(
        chat_id=chat_id,
        user_id=user_id,
    )

    if not result:
        await callback.answer(
            "Siz o‘yinda emassiz.",
            show_alert=True,
        )
        return

    await callback.answer(
        "O‘yindan chiqdingiz."
    )

    await callback.message.answer(
        player_leave_message(
            callback.from_user.first_name
        )
    )


# ============================================================
# CALLBACK — PLAYERS
# ============================================================

@router.callback_query(F.data == "game_players")
async def game_players_callback(
    callback: CallbackQuery,
):

    if callback.message is None:
        return

    chat_id = callback.message.chat.id

    players = await get_players(chat_id)

    await callback.answer()

    await callback.message.answer(
        player_list_message(players)
    )


# ============================================================
# CALLBACK — START GAME
# ============================================================

@router.callback_query(F.data == "game_start")
async def game_start_callback(
    callback: CallbackQuery,
):

    if callback.message is None:
        return

    chat_id = callback.message.chat.id

    member = await callback.bot.get_chat_member(
        chat_id,
        callback.from_user.id,
    )

    if member.status not in {
        "administrator",
        "creator",
    }:
        await callback.answer(
            "Faqat administrator o‘yinni boshlashi mumkin.",
            show_alert=True,
        )
        return

    players = await get_players(chat_id)

    if len(players) < MIN_PLAYERS:
        await callback.answer(
            f"Kamida {MIN_PLAYERS} ta o‘yinchi kerak.",
            show_alert=True,
        )
        return

    result = await start_game(
        chat_id=chat_id,
        admin_id=callback.from_user.id,
    )

    if not result:
        await callback.answer(
            "O‘yinni boshlashning imkoni bo‘lmadi.",
            show_alert=True,
        )
        return

    await callback.answer(
        "👑 O‘yin boshlandi!"
    )

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        game_start_message()
    )

    await callback.message.answer(
        night_message()
    )


# ============================================================
# CALLBACK — STATUS
# ============================================================

@router.callback_query(F.data == "game_status")
async def game_status_callback(
    callback: CallbackQuery,
):

    if callback.message is None:
        return

    chat_id = callback.message.chat.id

    game = await get_game(chat_id)

    if not game:
        await callback.answer(
            "Faol o‘yin yo‘q.",
            show_alert=True,
        )
        return

    players = await get_players(chat_id)
    alive = await get_alive_game_players(chat_id)

    status = game.get(
        "status",
        "unknown",
    )

    await callback.answer()

    await callback.message.answer(
        "👑 THRONE — O‘YIN HOLATI\n\n"
        f"📌 Bosqich: {status}\n"
        f"👥 O‘yinchilar: {len(players)}\n"
        f"❤️ Tiriklar: {len(alive)}\n"
        f"💀 Chiqarilganlar: {len(players) - len(alive)}",
        reply_markup=game_control_keyboard(),
    )


# ============================================================
# CALLBACK — STOP GAME
# ============================================================

@router.callback_query(F.data == "game_stop")
async def game_stop_callback(
    callback: CallbackQuery,
):

    if callback.message is None:
        return

    chat_id = callback.message.chat.id

    member = await callback.bot.get_chat_member(
        chat_id,
        callback.from_user.id,
    )

    if member.status not in {
        "administrator",
        "creator",
    }:
        await callback.answer(
            "Faqat administrator.",
            show_alert=True,
        )
        return

    result = await stop_game(
        chat_id=chat_id,
        admin_id=callback.from_user.id,
    )

    if not result:
        await callback.answer(
            "O‘yinni to‘xtatib bo‘lmadi.",
            show_alert=True,
        )
        return

    await callback.answer(
        "O‘yin to‘xtatildi."
    )

    await callback.message.answer(
        game_stop_message()
    )


# ============================================================
# CALLBACK — VOTING TARGET
# ============================================================

@router.callback_query(F.data.startswith("vote:"))
async def vote_callback(
    callback: CallbackQuery,
):

    if callback.message is None:
        return

    try:
        target_id = int(
            callback.data.split(":")[1]
        )
    except (
        ValueError,
        IndexError,
    ):
        await callback.answer(
            "Noto‘g‘ri ovoz.",
            show_alert=True,
        )
        return

    chat_id = callback.message.chat.id
    voter_id = callback.from_user.id

    game = await get_game(chat_id)

    if not game:
        await callback.answer(
            "Faol o‘yin yo‘q.",
            show_alert=True,
        )
        return

    if game.get("status") != "voting":
        await callback.answer(
            "Hozir ovoz berish bosqichi emas.",
            show_alert=True,
        )
        return

    if voter_id == target_id:
        await callback.answer(
            "O‘zingizga ovoz bera olmaysiz.",
            show_alert=True,
        )
        return

    try:
        from database import add_game_vote

        result = await add_game_vote(
            chat_id=chat_id,
            game_id=game["id"],
            voter_id=voter_id,
            target_id=target_id,
        )
    except Exception:
        result = False

    if not result:
        await callback.answer(
            "Ovozingiz qabul qilinmadi.",
            show_alert=True,
        )
        return

    await callback.answer(
        "⚖️ Ovozingiz qabul qilindi."
    )

    await callback.message.answer(
        "⚖️ Ovoz qabul qilindi.\n"
        "Natija barcha ovozlar yakunlangach e’lon qilinadi."
    )


# ============================================================
# CALLBACK — LAST WORDS
# ============================================================

@router.callback_query(F.data == "last_words_write")
async def last_words_callback(
    callback: CallbackQuery,
):

    await callback.answer(
        "So‘nggi so‘zingizni oddiy xabar sifatida yuboring."
    )


# ============================================================
# TEXT — LAST WORDS
# ============================================================

@router.message(F.text)
async def last_words_text_handler(
    message: Message,
):

    if not is_group(message):
        return

    game = await get_game(
        message.chat.id
    )

    if not game:
        return

    if game.get("status") != "last_words":
        return

    try:
        alive = await get_alive_game_players(
            message.chat.id
        )
    except Exception:
        alive = []

    user_id = message.from_user.id

    for player in alive:
        if int(player["user_id"]) == int(user_id):
            return

    try:
        from game_engine import create_last_words

        result = await create_last_words(
            chat_id=message.chat.id,
            user_id=user_id,
            text=message.text,
        )
    except Exception:
        result = False

    if not result:
        return

    await message.answer(
        last_words_message(
            message.from_user.first_name,
            message.text,
        )
    )


# ============================================================
# /PLAYERS
# ============================================================

@router.message(Command("players"))
async def players_command(
    message: Message,
):

    if not is_group(message):
        return

    players = await get_players(
        message.chat.id
    )

    if not players:
        await message.answer(
            "👥 Hozircha o‘yinchilar yo‘q."
        )
        return

    await message.answer(
        player_list_message(players)
    )


# ============================================================
# /GAME
# ============================================================

@router.message(Command("game"))
async def game_command(
    message: Message,
):

    if not is_group(message):
        return

    game = await get_game(
        message.chat.id
    )

    if not game:
        await message.answer(
            "⚠️ Faol THRONE o‘yini yo‘q."
        )
        return

    players = await get_players(
        message.chat.id
    )

    await message.answer(
        lobby_message(game),
        reply_markup=game_lobby_keyboard(
            can_start=len(players) >= MIN_PLAYERS
        ),
    )


# ============================================================
# CALLBACK — GAME RULES
# ============================================================

@router.callback_query(F.data == "game_rules")
async def game_rules_callback(
    callback: CallbackQuery,
):

    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "📖 THRONE O‘YIN QOIDALARI\n\n"
            f"👥 Minimal o‘yinchi: {MIN_PLAYERS}\n"
            f"👥 Maksimal o‘yinchi: {MAX_PLAYERS}\n\n"
            "🌙 Tunda rollar yashirin harakat qiladi.\n"
            "☀️ Kunduzi muhokama bo‘ladi.\n"
            "⚖️ So‘ng ovoz beriladi.\n"
            "🕯️ Chiqarilgan o‘yinchiga so‘nggi so‘z beriladi.\n\n"
            "👑 G‘alaba uchun o‘z tomoningizning maqsadini "
            "bajaring."
        )


# ============================================================
# CALLBACK — GAME ROLES
# ============================================================

@router.callback_query(F.data == "game_roles")
async def game_roles_callback(
    callback: CallbackQuery,
):

    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "🎭 THRONE\n\n"
            "O‘yinda jami 35 xil rol mavjud.\n\n"
            "👑 Taxt\n"
            "🩸 Qora\n"
            "🏴 Isyon\n"
            "☠️ Mustaqil\n\n"
            "Har bir rolning o‘z vazifasi va g‘alaba "
            "sharti mavjud."
      )
