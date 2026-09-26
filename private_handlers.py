# ============================================================
# THRONE — PRIVATE HANDLERS
# ============================================================

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import CREATOR_ID
from database import (
    get_user,
    create_user,
    get_player_stats,
    get_inventory,
    get_kingdom,
    get_castle,
    get_army,
    get_daily_reward,
    get_mini_profile,
)

from keyboards import (
    main_menu_keyboard,
    cabinet_keyboard,
    kingdom_keyboard,
    castle_keyboard,
    throne_keyboard,
    army_keyboard,
    inventory_keyboard,
    shop_keyboard,
    clan_keyboard,
    family_keyboard,
    competitions_keyboard,
    roles_keyboard,
    rewards_keyboard,
    black_market_keyboard,
    elite_keyboard,
    language_keyboard,
    ai_keyboard,
    help_keyboard,
    settings_keyboard,
    back_keyboard,
)


router = Router(name="throne_private_handlers")


# ============================================================
# PRIVATE CHAT CHECK
# ============================================================

def is_private(message: Message) -> bool:
    return message.chat.type == "private"


# ============================================================
# ENSURE USER
# ============================================================

async def ensure_user(message: Message):
    user = message.from_user

    if user is None:
        return None

    data = await get_user(user.id)

    if data is None:
        await create_user(
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
        )

        data = await get_user(user.id)

    return data


# ============================================================
# CABINET
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "👤 KABINET",
)
async def private_cabinet(message: Message):

    await ensure_user(message)

    user = message.from_user

    if user is None:
        return

    if user.id == CREATOR_ID:
        balance_text = (
            "🟡 Oltin: ∞\n"
            "🪙 Coin: ∞\n"
            "💎 Olmos: ∞\n"
            "⚜️ Elite Pass: AKTIV ∞"
        )
    else:
        balance_text = (
            "🟡 Oltin: 0\n"
            "🪙 Coin: 0\n"
            "💎 Olmos: 0"
        )

    await message.answer(
        "👤 KABINET\n\n"
        f"🪪 Nik: {user.first_name or 'O‘yinchi'}\n"
        f"🆔 ID: {user.id}\n\n"
        f"{balance_text}\n\n"
        "THRONE profilingiz:",
        reply_markup=cabinet_keyboard(),
    )


# ============================================================
# PROFILE STATS
# ============================================================

@router.callback_query(
    F.data == "cabinet_stats"
)
async def private_profile_stats(
    callback: CallbackQuery,
):

    await callback.answer()

    user_id = callback.from_user.id

    try:
        stats = await get_player_stats(user_id)
    except Exception:
        stats = None

    if not stats:
        text = (
            "📊 STATISTIKA\n\n"
            "Hozircha statistika mavjud emas."
        )
    else:
        text = (
            "📊 SHAXSIY STATISTIKA\n\n"
            f"🏆 Reyting: {stats.get('rating', 0)}\n"
            f"⚔️ O‘yinlar: {stats.get('games_played', 0)}\n"
            f"👑 G‘alabalar: {stats.get('wins', 0)}\n"
            f"💀 Mag‘lubiyatlar: {stats.get('losses', 0)}\n"
            f"⭐ Ochko: {stats.get('points', 0)}"
        )

    if callback.message:
        await callback.message.answer(
            text,
            reply_markup=back_keyboard(),
        )


# ============================================================
# KINGDOM
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "🏰 QIROLLIGIM",
)
async def private_kingdom(
    message: Message,
):

    await ensure_user(message)

    kingdom = await get_kingdom(
        message.from_user.id
    )

    if kingdom:
        kingdom_name = kingdom.get(
            "name",
            "Noma’lum qirollik",
        )
    else:
        kingdom_name = "Hali yaratilmagan"

    await message.answer(
        "🏰 QIROLLIGIM\n\n"
        f"👑 Qirollik: {kingdom_name}\n\n"
        "Qirolligingizni boshqaring:",
        reply_markup=kingdom_keyboard(),
    )


# ============================================================
# CASTLE
# ============================================================

@router.callback_query(
    F.data == "kingdom_castle"
)
async def private_castle(
    callback: CallbackQuery,
):

    await callback.answer()

    castle = await get_castle(
        callback.from_user.id
    )

    if castle:
        level = castle.get("level", 1)
        defense = castle.get("defense", 0)
        guards = castle.get("guards", 0)
    else:
        level = 1
        defense = 0
        guards = 0

    if callback.message:
        await callback.message.answer(
            "🏰 QAL’A\n\n"
            f"⭐ Daraja: {level}\n"
            f"🛡️ Himoya: {defense}\n"
            f"👥 Qo‘riqchilar: {guards}\n\n"
            "Qal’angizni rivojlantiring.",
            reply_markup=castle_keyboard(),
        )


# ============================================================
# THRONE
# ============================================================

@router.callback_query(
    F.data == "kingdom_throne"
)
async def private_throne(
    callback: CallbackQuery,
):

    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "👑 TAХT\n\n"
            "🏛️ Saroy\n"
            "📜 Farmonlar\n"
            "⚖️ Qarorlar\n\n"
            "Qirollik boshqaruvi shu bo‘lim orqali amalga "
            "oshiriladi.",
            reply_markup=throne_keyboard(),
        )


# ============================================================
# ARMY
# ============================================================

@router.callback_query(
    F.data == "kingdom_army"
)
async def private_army(
    callback: CallbackQuery,
):

    await callback.answer()

    army = await get_army(
        callback.from_user.id
    )

    if army:
        soldiers = army.get("soldiers", 0)
        archers = army.get("archers", 0)
        guards = army.get("guards", 0)
        cavalry = army.get("cavalry", 0)
    else:
        soldiers = 0
        archers = 0
        guards = 0
        cavalry = 0

    if callback.message:
        await callback.message.answer(
            "⚔️ ARMIYA\n\n"
            f"⚔️ Askarlar: {soldiers}\n"
            f"🏹 Kamonchilar: {archers}\n"
            f"🛡️ Qo‘riqchilar: {guards}\n"
            f"🐎 Suvariylar: {cavalry}\n\n"
            "Qo‘shinlaringizni rivojlantiring.",
            reply_markup=army_keyboard(),
        )


# ============================================================
# INVENTORY
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "🎒 INVENTAR",
)
async def private_inventory(
    message: Message,
):

    await ensure_user(message)

    items = await get_inventory(
        message.from_user.id
    )

    if not items:
        text = (
            "🎒 INVENTAR\n\n"
            "Hozircha inventaringiz bo‘sh.\n\n"
            "💰 DO‘KON orqali yangi buyumlar olishingiz mumkin."
        )
    else:
        lines = ["🎒 INVENTAR", ""]

        for item in items[:30]:
            name = item.get(
                "name",
                "Noma’lum buyum",
            )
            quantity = item.get(
                "quantity",
                1,
            )

            lines.append(
                f"• {name} × {quantity}"
            )

        text = "\n".join(lines)

    await message.answer(
        text,
        reply_markup=inventory_keyboard(),
    )


# ============================================================
# SHOP
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "💰 DO‘KON",
)
async def private_shop(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "💰 THRONE DO‘KONI\n\n"
        "⚔️ Qurollar\n"
        "🛡️ Zirhlar\n"
        "👕 Kiyimlar\n"
        "🐎 Otlar\n"
        "🎁 Sovg‘alar\n"
        "💎 Premium buyumlar\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=shop_keyboard(),
    )


# ============================================================
# CLAN
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "🏴 KLANIM",
)
async def private_clan(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "🏴 KLANIM\n\n"
        "Klaningizni boshqaring.\n\n"
        "👥 A’zolar\n"
        "⚔️ Klan urushi\n"
        "💰 Klan xazinasi\n"
        "🏆 Klan reytingi",
        reply_markup=clan_keyboard(),
    )


# ============================================================
# FAMILY
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "❤️ OILA",
)
async def private_family(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "❤️ OILA\n\n"
        "Oila, nikoh va oilaviy statistikani boshqaring.\n\n"
        "💍 Nikoh guruh orqali amalga oshiriladi.",
        reply_markup=family_keyboard(),
    )


# ============================================================
# COMPETITIONS
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "🏆 MUSOBAQALAR",
)
async def private_competitions(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "🏆 MUSOBAQALAR\n\n"
        "👑 THRONE turnirlari va ⚔️ duellar:",
        reply_markup=competitions_keyboard(),
    )


# ============================================================
# ROLES
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "🎭 ROLLAR",
)
async def private_roles(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "🎭 THRONE ROLLARI\n\n"
        "Guruh o‘yinidagi 35 ta rol to‘rt tomonga "
        "bo‘lingan:",
        reply_markup=roles_keyboard(),
    )


# ============================================================
# RANKING
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "📊 REYTING",
)
async def private_ranking(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "📊 THRONE REYTINGI\n\n"
        "🏆 Eng kuchli o‘yinchilar\n"
        "⚔️ G‘alabalar\n"
        "⭐ Reyting ochkolari\n"
        "👑 THRONE darajasi\n\n"
        "Reyting tizimi o‘yin natijalariga qarab "
        "yangilanadi.",
        reply_markup=back_keyboard(),
    )


# ============================================================
# REWARDS
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "🎁 BONUSLAR",
)
async def private_rewards(
    message: Message,
):

    await ensure_user(message)

    reward = await get_daily_reward(
        message.from_user.id
    )

    if reward:
        status = "🎁 Kunlik bonus mavjud."
    else:
        status = "🎁 Kunlik bonusga tayyorlaning."

    await message.answer(
        "🎁 BONUSLAR\n\n"
        f"{status}\n\n"
        "🏆 Reyting mukofotlari\n"
        "🎁 Sovg‘alar\n"
        "⭐ Maxsus bonuslar",
        reply_markup=rewards_keyboard(),
    )


# ============================================================
# BLACK MARKET
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "🕶️ QORA BOZOR",
)
async def private_black_market(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "🕶️ QORA BOZOR\n\n"
        "Bu yerda oddiy do‘konda mavjud bo‘lmagan "
        "maxsus va noyob takliflar paydo bo‘ladi.",
        reply_markup=black_market_keyboard(),
    )


# ============================================================
# ELITE
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "⚜️ THRONE ELITE",
)
async def private_elite(
    message: Message,
):

    await ensure_user(message)

    if message.from_user.id == CREATOR_ID:
        await message.answer(
            "⚜️ THRONE ELITE\n\n"
            "𓆩 ELITE YARATUVCHI 𓆪\n\n"
            "⚜️ Elite Pass: AKTIV ∞\n"
            "💎 Barcha premium imkoniyatlar: AKTIV",
            reply_markup=elite_keyboard(),
        )
        return

    await message.answer(
        "⚜️ THRONE ELITE\n\n"
        "Premium imkoniyatlardan foydalanish uchun "
        "Elite muddatini tanlang:",
        reply_markup=elite_keyboard(),
    )


# ============================================================
# LANGUAGE
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "🌐 TIL",
)
async def private_language(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "🌐 THRONE TILI\n\n"
        "O‘zingizga qulay tilni tanlang:",
        reply_markup=language_keyboard(),
    )


# ============================================================
# LANGUAGE CALLBACK
# ============================================================

@router.callback_query(
    F.data.startswith("lang_")
)
async def private_language_callback(
    callback: CallbackQuery,
):

    language = callback.data.replace(
        "lang_",
        "",
    )

    names = {
        "uz": "🇺🇿 O‘zbek",
        "ru": "🇷🇺 Русский",
        "en": "🇬🇧 English",
        "tr": "🇹🇷 Türkçe",
        "ar": "🇸🇦 العربية",
        "ky": "🇰🇬 Кыргызча",
    }

    await callback.answer(
        f"{names.get(language, 'Til')} tanlandi."
    )

    if callback.message:
        await callback.message.answer(
            f"🌐 Tanlangan til: "
            f"{names.get(language, 'Noma’lum')}\n\n"
            "Til sozlamasi THRONE menyulari va "
            "o‘yin interfeysiga qo‘llanadi.",
            reply_markup=back_keyboard(),
        )


# ============================================================
# AI
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "🤖 THRONE AI",
)
async def private_ai(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "🤖 THRONE AI\n\n"
        "Men sizga THRONE tizimlari bo‘yicha yordam "
        "beraman.\n\n"
        "👤 Profil\n"
        "💰 Balans\n"
        "🏰 Qirollik\n"
        "⚔️ O‘yin\n"
        "🏴 Klan\n"
        "🎭 Rollar",
        reply_markup=ai_keyboard(),
    )


# ============================================================
# HELP
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "❓ YORDAM",
)
async def private_help(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "❓ THRONE YORDAM\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=help_keyboard(),
    )


# ============================================================
# SETTINGS
# ============================================================

@router.message(
    F.chat.type == "private",
    F.text == "⚙️ SOZLAMALAR",
)
async def private_settings(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "⚙️ SOZLAMALAR\n\n"
        "THRONE sozlamalarini boshqaring:",
        reply_markup=settings_keyboard(),
    )


# ============================================================
# MINI PROFILE
# ============================================================

@router.callback_query(
    F.data == "cabinet_appearance"
)
async def mini_profile_callback(
    callback: CallbackQuery,
):

    await callback.answer()

    profile = await get_mini_profile(
        callback.from_user.id
    )

    if profile:
        level = profile.get(
            "level",
            1,
        )
        character = profile.get(
            "character",
            "Tanlanmagan",
        )
    else:
        level = 1
        character = "Tanlanmagan"

    if callback.message:
        await callback.message.answer(
            "🎭 PROFIL KO‘RINISHI\n\n"
            f"⭐ Daraja: {level}\n"
            f"👤 Qahramon: {character}\n\n"
            "Mini App orqali avatar, kiyim, qurol va "
            "boshqa ko‘rinishlarni boshqarish mumkin.",
            reply_markup=back_keyboard(),
        )


# ============================================================
# /WALLET
# ============================================================

@router.message(
    Command("wallet"),
    F.chat.type == "private",
)
async def private_wallet(
    message: Message,
):

    await ensure_user(message)

    if message.from_user.id == CREATOR_ID:
        text = (
            "💰 HAMYON\n\n"
            "🟡 Oltin: ∞\n"
            "🪙 Coin: ∞\n"
            "💎 Olmos: ∞\n"
            "⚜️ Elite: ∞"
        )
    else:
        text = (
            "💰 HAMYON\n\n"
            "🟡 Oltin: 0\n"
            "🪙 Coin: 0\n"
            "💎 Olmos: 0"
        )

    await message.answer(
        text,
        reply_markup=back_keyboard(),
    )


# ============================================================
# /GOLD
# ============================================================

@router.message(
    Command("gold"),
    F.chat.type == "private",
)
async def private_gold(
    message: Message,
):

    await ensure_user(message)

    value = "∞" if message.from_user.id == CREATOR_ID else "0"

    await message.answer(
        f"🟡 OLTIN\n\n"
        f"Balansingiz: {value}",
        reply_markup=back_keyboard(),
    )


# ============================================================
# /COIN
# ============================================================

@router.message(
    Command("coin"),
    F.chat.type == "private",
)
async def private_coin(
    message: Message,
):

    await ensure_user(message)

    value = "∞" if message.from_user.id == CREATOR_ID else "0"

    await message.answer(
        f"🪙 COIN\n\n"
        f"Balansingiz: {value}",
        reply_markup=back_keyboard(),
    )


# ============================================================
# /DIAMOND
# ============================================================

@router.message(
    Command("diamond"),
    F.chat.type == "private",
)
async def private_diamond(
    message: Message,
):

    await ensure_user(message)

    value = "∞" if message.from_user.id == CREATOR_ID else "0"

    await message.answer(
        f"💎 OLMOS\n\n"
        f"Balansingiz: {value}",
        reply_markup=back_keyboard(),
    )


# ============================================================
# /DAILY
# ============================================================

@router.message(
    Command("daily"),
    F.chat.type == "private",
)
async def private_daily(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "🎁 KUNLIK BONUS\n\n"
        "Kunlik bonus tizimi shu yerda ishlaydi.",
        reply_markup=rewards_keyboard(),
    )


# ============================================================
# UNKNOWN PRIVATE MESSAGE
# ============================================================

@router.message(
    F.chat.type == "private"
)
async def private_unknown(
    message: Message,
):

    await ensure_user(message)

    await message.answer(
        "👑 THRONE\n\n"
        "Kerakli bo‘limni asosiy menyu
