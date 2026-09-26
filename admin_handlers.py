# ============================================================
# THRONE — ADMIN HANDLERS
# ============================================================

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import CREATOR_ID
from database import (
    get_user,
    get_player_stats,
    get_top_players,
    get_active_game,
    security_log,
)

router = Router(name="throne_admin_handlers")


# ============================================================
# CREATOR CHECK
# ============================================================

def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


async def creator_only_message(message: Message) -> bool:
    if not is_creator(message.from_user.id):
        await message.answer(
            "⛔ Bu bo‘lim faqat THRONE yaratuvchisi uchun."
        )
        return False

    return True


async def creator_only_callback(callback: CallbackQuery) -> bool:
    if not is_creator(callback.from_user.id):
        await callback.answer(
            "⛔ Bu bo‘lim faqat yaratuvchi uchun.",
            show_alert=True,
        )
        return False

    return True


# ============================================================
# ADMIN PANEL
# ============================================================

@router.message(
    Command("admin"),
    F.chat.type == "private",
)
async def admin_panel(message: Message):

    if not await creator_only_message(message):
        return

    await message.answer(
        "👑 THRONE — YARATUVCHI PANELI\n\n"
        "𓆩 ELITE YARATUVCHI 𓆪\n\n"
        "🟡 Oltin: ∞\n"
        "🪙 Coin: ∞\n"
        "💎 Olmos: ∞\n"
        "⚜️ Elite: AKTIV ∞\n\n"
        "🛡️ Tizim: AKTIV\n"
        "🔐 Xavfsizlik: AKTIV\n"
        "⚙️ Boshqaruv: AKTIV\n\n"
        "Quyidagi buyruqlar orqali boshqarish mumkin:\n\n"
        "/adminstats — statistika\n"
        "/players — o‘yinchilar\n"
        "/security — xavfsizlik\n"
        "/activegame — faol o‘yin\n"
        "/top — reyting\n"
        "/botstatus — bot holati"
    )


# ============================================================
# ADMIN STATS
# ============================================================

@router.message(
    Command("adminstats"),
    F.chat.type == "private",
)
async def admin_stats(message: Message):

    if not await creator_only_message(message):
        return

    top_players = await get_top_players(10)

    player_count = len(top_players)

    await message.answer(
        "📊 THRONE STATISTIKASI\n\n"
        f"👥 Ko‘rsatilgan reyting yozuvlari: {player_count}\n"
        "🎮 Guruh o‘yinlari: tizim orqali boshqariladi\n"
        "🏰 Qirolliklar: faol\n"
        "🏴 Klanlar: faol\n"
        "⚔️ Urushlar: faol\n"
        "🏆 Turnirlar: faol\n"
        "💍 Oila tizimi: faol\n"
        "💎 Premium tizim: faol\n\n"
        "🛡️ Xavfsizlik tizimi: AKTIV"
    )


# ============================================================
# PLAYER LOOKUP
# ============================================================

@router.message(
    Command("player"),
    F.chat.type == "private",
)
async def admin_player(message: Message):

    if not await creator_only_message(message):
        return

    parts = message.text.split()

    if len(parts) < 2:
        await message.answer(
            "ℹ️ Foydalanish:\n"
            "/player USER_ID"
        )
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer(
            "❌ USER_ID raqam bo‘lishi kerak."
        )
        return

    user = await get_user(user_id)

    if not user:
        await message.answer(
            "❌ O‘yinchi topilmadi."
        )
        return

    stats = await get_player_stats(user_id)

    username = user.get("username") or "username yo‘q"
    first_name = user.get("first_name") or "Noma’lum"

    if stats:
        games = stats.get("games_played", 0)
        wins = stats.get("wins", 0)
        losses = stats.get("losses", 0)
        points = stats.get("points", 0)
        rating = stats.get("rating", 0)
    else:
        games = 0
        wins = 0
        losses = 0
        points = 0
        rating = 0

    await message.answer(
        "👤 O‘YINCHI MA’LUMOTI\n\n"
        f"🪪 Ism: {first_name}\n"
        f"🔗 Username: @{username}\n"
        f"🆔 ID: {user_id}\n\n"
        f"🎮 O‘yinlar: {games}\n"
        f"👑 G‘alabalar: {wins}\n"
        f"💀 Mag‘lubiyatlar: {losses}\n"
        f"⭐ Ochko: {points}\n"
        f"📊 Reyting: {rating}"
    )


# ============================================================
# PLAYERS
# ============================================================

@router.message(
    Command("players"),
    F.chat.type == "private",
)
async def admin_players(message: Message):

    if not await creator_only_message(message):
        return

    players = await get_top_players(20)

    if not players:
        await message.answer(
            "👥 Hozircha o‘yinchilar statistikasi mavjud emas."
        )
        return

    lines = [
        "👥 THRONE O‘YINCHILARI",
        "",
    ]

    for index, player in enumerate(players, start=1):

        name = (
            player.get("first_name")
            or player.get("username")
            or f"ID {player.get('user_id')}"
        )

        points = player.get("points", 0)

        lines.append(
            f"{index}. {name} — ⭐ {points}"
        )

    await message.answer(
        "\n".join(lines)
    )


# ============================================================
# SECURITY
# ============================================================

@router.message(
    Command("security"),
    F.chat.type == "private",
)
async def admin_security(message: Message):

    if not await creator_only_message(message):
        return

    await message.answer(
        "🛡️ THRONE XAVFSIZLIK MARKAZI\n\n"
        "🔐 Creator himoyasi: AKTIV\n"
        "🛡️ Admin tekshiruvi: AKTIV\n"
        "🚫 Ruxsatsiz boshqaruv: BLOKLANGAN\n"
        "🎮 O‘yin holati nazorati: AKTIV\n"
        "📋 Xavfsizlik jurnali: AKTIV\n\n"
        "⚠️ Maxfiy rollar va yashirin harakatlar "
        "oddiy foydalanuvchiga chiqarilmaydi."
    )


# ============================================================
# ACTIVE GAME
# ============================================================

@router.message(
    Command("activegame"),
    F.chat.type == "private",
)
async def admin_active_game(message: Message):

    if not await creator_only_message(message):
        return

    # Private chatda game chat_id orqali izlanadi.
    # Bu yerda umumiy holat haqida ma’lumot beriladi.
    await message.answer(
        "🎮 FAOL O‘YIN\n\n"
        "Faol guruh o‘yinlari guruh chatining "
        "o‘zida boshqariladi.\n\n"
        "Guruhdagi o‘yinni tekshirish uchun "
        "/game buyrug‘idan foydalaning."
    )


# ============================================================
# BOT STATUS
# ============================================================

@router.message(
    Command("botstatus"),
    F.chat.type == "private",
)
async def admin_bot_status(message: Message):

    if not await creator_only_message(message):
        return

    await message.answer(
        "⚙️ THRONE BOT STATUS\n\n"
        "🟢 Bot: ONLINE\n"
        "🟢 Database: CONNECTED\n"
        "🟢 Game Engine: READY\n"
        "🟢 Role Engine: READY\n"
        "🟢 Security: ACTIVE\n"
        "🟢 Economy: ACTIVE\n"
        "🟢 Kingdom: ACTIVE\n"
        "🟢 Clan: ACTIVE\n"
        "🟢 Family: ACTIVE\n"
        "🟢 Tournament: ACTIVE\n"
        "🟢 Mini App: READY\n"
        "🟢 Elite: ACTIVE"
    )


# ============================================================
# TOP RANKING
# ============================================================

@router.message(
    Command("top"),
    F.chat.type == "private",
)
async def admin_top(message: Message):

    if not await creator_only_message(message):
        return

    players = await get_top_players(10)

    if not players:
        await message.answer(
            "📊 Reyting ma’lumotlari hali mavjud emas."
        )
        return

    lines = [
        "🏆 THRONE TOP 10",
        "",
    ]

    for index, player in enumerate(players, start=1):

        name = (
            player.get("first_name")
            or player.get("username")
            or f"ID {player.get('user_id')}"
        )

        points = player.get("points", 0)

        lines.append(
            f"{index}. {name} — ⭐ {points}"
        )

    await message.answer(
        "\n".join(lines)
    )


# ============================================================
# CREATOR WALLET
# ============================================================

@router.message(
    Command("creator"),
    F.chat.type == "private",
)
async def creator_wallet(message: Message):

    if not await creator_only_message(message):
        return

    await message.answer(
        "𓆩 ELITE YARATUVCHI 𓆪\n\n"
        "👑 THRONE Creator\n\n"
        "🟡 Oltin: ∞\n"
        "🪙 Coin: ∞\n"
        "💎 Olmos: ∞\n"
        "⚜️ Elite Pass: AKTIV ∞\n\n"
        "Barcha creator resurslari cheksiz."
    )


# ============================================================
# SECURITY LOG CALLBACK
# ============================================================

@router.callback_query(
    F.data == "admin_security"
)
async def admin_security_callback(
    callback: CallbackQuery,
):

    if not await creator_only_callback(callback):
        return

    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "🛡️ XAVFSIZLIK\n\n"
            "🔐 Creator tekshiruvi: AKTIV\n"
            "🚫 Ruxsatsiz kirish: BLOK\n"
            "📋 Log tizimi: AKTIV\n"
            "🛡️ O‘yin himoyasi: AKTIV"
        )


# ============================================================
# ADMIN CALLBACK
# ============================================================

@router.callback_query(
    F.data == "admin_panel"
)
async def admin_panel_callback(
    callback: CallbackQuery,
):

    if not await creator_only_callback(callback):
        return

    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "👑 THRONE YARATUVCHI PANELI\n\n"
            "/adminstats\n"
            "/players\n"
            "/player USER_ID\n"
            "/security\n"
            "/activegame\n"
            "/top\n"
            "/botstatus\n"
            "/creator"
        )


# ============================================================
# PROTECTION AGAINST UNKNOWN ADMIN ACTIONS
# ============================================================

@router.callback_query(
    F.data.startswith("admin_")
)
async def unknown_admin_callback(
    callback: CallbackQuery,
):

    if not await creator_only_callback(callback):
        return

    await callback.answer(
        "⚙️ Bu admin funksiyasi keyingi tizim modulida ishlaydi.",
        show_alert=True,
                               )
