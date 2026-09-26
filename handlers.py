# ============================================================
# THRONE — HANDLERS
# ============================================================

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery

from config import CREATOR_ID
from database import create_user, get_user

from keyboards import (
    main_menu_keyboard,
    back_keyboard,
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
)


router = Router(name="throne_handlers")


# ============================================================
# /START
# ============================================================

@router.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user

    if user is None:
        return

    await create_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        last_name=user.last_name or "",
    )

    if user.id == CREATOR_ID:
        text = (
            "👑 THRONE\n"
            "𓆩 ELITE YARATUVCHI 𓆪\n\n"
            "🟡 Oltin: ∞\n"
            "🪙 Coin: ∞\n"
            "💎 Olmos: ∞\n"
            "⚜️ Elite Pass: AKTIV ∞\n\n"
            "🏰 Sening hukmronliging shu yerdan boshlanadi."
        )
    else:
        name = user.first_name or "O‘yinchi"

        text = (
            f"👑 THRONE’ga xush kelibsiz, {name}!\n\n"
            "🏰 Bu oddiy o‘yin emas — bu toj, kuch va strategiya olami.\n\n"
            "⚔️ Kuchingizni oshiring.\n"
            "🏴 Klaningizni yarating.\n"
            "💎 Noyob imkoniyatlarni qo‘lga kiriting.\n"
            "👑 Taxt uchun kurashing.\n\n"
            "✨ THRONE — har bir qaror tarixga aylanadi."
        )

    await message.answer(
        text,
        reply_markup=main_menu_keyboard(),
    )


# ============================================================
# GENERAL COMMANDS
# ============================================================

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "❓ THRONE YORDAM\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=help_keyboard(),
    )


@router.message(Command("rules"))
async def rules_command(message: Message):
    await message.answer(
        "📖 THRONE QOIDALARI\n\n"
        "• Guruh o‘yinini faqat guruh administratori boshlaydi.\n"
        "• O‘yin uchun bot guruhda admin bo‘lishi kerak.\n"
        "• O‘yin davomida yashirin harakatlar oshkor qilinmaydi.\n"
        "• Ovoz berish natijasida eng ko‘p ovoz olgan o‘yinchi chiqariladi.\n"
        "• Teng ovoz bo‘lsa, qayta ovoz beriladi.\n"
        "• Ikkinchi marta ham tenglik bo‘lsa, hech kim chiqarilmaydi.\n"
        "• Chiqarilgan o‘yinchiga so‘nggi so‘z beriladi.\n\n"
        "👑 THRONE — har bir qaror tarixga aylanadi.",
        reply_markup=back_keyboard(),
    )


@router.message(Command("profile"))
async def profile_command(message: Message):
    await show_cabinet(message)


@router.message(Command("kingdom"))
async def kingdom_command(message: Message):
    await show_kingdom(message)


@router.message(Command("inventory"))
async def inventory_command(message: Message):
    await show_inventory(message)


@router.message(Command("shop"))
async def shop_command(message: Message):
    await show_shop(message)


@router.message(Command("clan"))
async def clan_command(message: Message):
    await show_clan(message)


@router.message(Command("clans"))
async def clan_command_2(message: Message):
    await show_clan(message)


@router.message(Command("daily"))
async def daily_command(message: Message):
    await show_rewards(message)


@router.message(Command("ranking"))
async def ranking_command(message: Message):
    await message.answer(
        "📊 REYTING\n\n"
        "Bu bo‘limda o‘yinchilar reytingi ko‘rsatiladi.",
        reply_markup=back_keyboard(),
    )


@router.message(Command("stats"))
async def stats_command(message: Message):
    await message.answer(
        "📊 STATISTIKA\n\n"
        "Shaxsiy o‘yin statistikangiz shu yerda ko‘rinadi.",
        reply_markup=back_keyboard(),
    )


# ============================================================
# MAIN MENU — TEXT BUTTONS
# ============================================================

@router.message(F.text == "👤 KABINET")
async def cabinet_message(message: Message):
    await show_cabinet(message)


@router.message(F.text == "🏰 QIROLLIGIM")
async def kingdom_message(message: Message):
    await show_kingdom(message)


@router.message(F.text == "🎒 INVENTAR")
async def inventory_message(message: Message):
    await show_inventory(message)


@router.message(F.text == "💰 DO‘KON")
async def shop_message(message: Message):
    await show_shop(message)


@router.message(F.text == "🏴 KLANIM")
async def clan_message(message: Message):
    await show_clan(message)


@router.message(F.text == "❤️ OILA")
async def family_message(message: Message):
    await show_family(message)


@router.message(F.text == "⚔️ KUCHLARIM")
async def army_message(message: Message):
    await message.answer(
        "⚔️ KUCHLARIM\n\n"
        "Bu yerda shaxsiy kuchingiz va harbiy ko‘rsatkichlaringiz "
        "boshqariladi.",
        reply_markup=army_keyboard(),
    )


@router.message(F.text == "🏆 MUSOBAQALAR")
async def competitions_message(message: Message):
    await message.answer(
        "🏆 MUSOBAQALAR\n\n"
        "THRONE’dagi musobaqalar va duellar:",
        reply_markup=competitions_keyboard(),
    )


@router.message(F.text == "🎭 ROLLAR")
async def roles_message(message: Message):
    await message.answer(
        "🎭 THRONE ROLLARI\n\n"
        "Guruh o‘yinidagi barcha rollar:",
        reply_markup=roles_keyboard(),
    )


@router.message(F.text == "📊 REYTING")
async def ranking_message(message: Message):
    await message.answer(
        "📊 REYTING\n\n"
        "Eng yuqori natijalarga ega o‘yinchilar shu yerda "
        "ko‘rsatiladi.",
        reply_markup=back_keyboard(),
    )


@router.message(F.text == "🎁 BONUSLAR")
async def rewards_message(message: Message):
    await show_rewards(message)


@router.message(F.text == "🕶️ QORA BOZOR")
async def black_market_message(message: Message):
    await message.answer(
        "🕶️ QORA BOZOR\n\n"
        "Bu yerda oddiy bozorda uchramaydigan maxsus "
        "takliflar paydo bo‘ladi.",
        reply_markup=black_market_keyboard(),
    )


@router.message(F.text == "⚜️ THRONE ELITE")
async def elite_message(message: Message):
    await message.answer(
        "⚜️ THRONE ELITE\n\n"
        "Elite imkoniyatlarini tanlang:",
        reply_markup=elite_keyboard(),
    )


@router.message(F.text == "🌐 TIL")
async def language_message(message: Message):
    await message.answer(
        "🌐 TILNI TANLANG:",
        reply_markup=language_keyboard(),
    )


@router.message(F.text == "🤖 THRONE AI")
async def ai_message(message: Message):
    await message.answer(
        "🤖 THRONE AI\n\n"
        "Qirollik, o‘yin, klan, inventar va boshqa "
        "THRONE tizimlari bo‘yicha yordam:",
        reply_markup=ai_keyboard(),
    )


@router.message(F.text == "❓ YORDAM")
async def help_message(message: Message):
    await message.answer(
        "❓ THRONE YORDAM\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=help_keyboard(),
    )


@router.message(F.text == "⚙️ SOZLAMALAR")
async def settings_message(message: Message):
    await message.answer(
        "⚙️ SOZLAMALAR\n\n"
        "THRONE sozlamalarini boshqaring:",
        reply_markup=settings_keyboard(),
    )


# ============================================================
# SECTION FUNCTIONS
# ============================================================

async def show_cabinet(message: Message):
    user = message.from_user

    if user is None:
        return

    data = await get_user(user.id)

    if data is None:
        await create_user(
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
        )

    if user.id == CREATOR_ID:
        balance = (
            "🟡 Oltin: ∞\n"
            "🪙 Coin: ∞\n"
            "💎 Olmos: ∞\n"
            "⚜️ Elite: AKTIV ∞"
        )
    else:
        balance = (
            "🟡 Oltin: 0\n"
            "🪙 Coin: 0\n"
            "💎 Olmos: 0"
        )

    await message.answer(
        f"👤 KABINET\n\n"
        f"🪪 Nik: {user.first_name or 'O‘yinchi'}\n"
        f"🆔 ID: {user.id}\n\n"
        f"{balance}\n\n"
        "Quyidagi bo‘limlardan birini tanlang:",
        reply_markup=cabinet_keyboard(),
    )


async def show_kingdom(message: Message):
    await message.answer(
        "🏰 QIROLLIGIM\n\n"
        "👑 Sizning qirolligingiz shu yerda boshqariladi.\n\n"
        "Qal’a, taxt, armiya, hudud va urushlarni "
        "boshqaring.",
        reply_markup=kingdom_keyboard(),
    )


async def show_inventory(message: Message):
    await message.answer(
        "🎒 INVENTAR\n\n"
        "Qurollar, zirhlar, kiyimlar, otlar va sovg‘alaringiz.",
        reply_markup=inventory_keyboard(),
    )


async def show_shop(message: Message):
    await message.answer(
        "💰 DO‘KON\n\n"
        "THRONE do‘konidan kerakli buyumlarni tanlang.",
        reply_markup=shop_keyboard(),
    )


async def show_clan(message: Message):
    await message.answer(
        "🏴 KLANIM\n\n"
        "Klaningizni boshqaring, a’zolarni ko‘ring va "
        "klan urushlarida qatnashing.",
        reply_markup=clan_keyboard(),
    )


async def show_family(message: Message):
    await message.answer(
        "❤️ OILA\n\n"
        "Oilaviy holatingiz, nikoh va oilaviy statistikangiz.",
        reply_markup=family_keyboard(),
    )


async def show_rewards(message: Message):
    await message.answer(
        "🎁 BONUSLAR\n\n"
        "Kunlik bonus, reyting mukofotlari va sovg‘alar.",
        reply_markup=rewards_keyboard(),
    )


# ============================================================
# CALLBACK — BACK
# ============================================================

@router.callback_query(F.data == "back_main")
async def back_main_callback(callback: CallbackQuery):
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "👑 THRONE ASOSIY MENYUSI",
            reply_markup=main_menu_keyboard(),
        )


# ============================================================
# CALLBACK — CABINET
# ============================================================

@router.callback_query(F.data == "cabinet_stats")
async def cabinet_stats_callback(callback: CallbackQuery):
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "📊 STATISTIKA\n\n"
            "O‘yinlar, g‘alabalar, mag‘lubiyatlar va "
            "reyting ko‘rsatkichlari shu yerda bo‘ladi.",
            reply_markup=back_keyboard(),
        )


@router.callback_query(F.data == "cabinet_achievements")
async def cabinet_achievements_callback(callback: CallbackQuery):
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "🏅 YUTUQLAR\n\n"
            "Siz qo‘lga kiritgan yutuqlar shu yerda ko‘rsatiladi.",
            reply_markup=back_keyboard(),
        )


# ============================================================
# CALLBACK — KINGDOM
# ============================================================

@router.callback_query(F.data == "kingdom_main")
async def kingdom_main_callback(callback: CallbackQuery):
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "🏰 QIROLLIGIM",
            reply_markup=kingdom_keyboard(),
        )


@router.callback_query(F.data == "kingdom_castle")
async def kingdom_castle_callback(callback: CallbackQuery):
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "🏰 QAL’A\n\n"
            "Qal’a darajasi, himoya, qo‘riqchilar va xazina.",
            reply_markup=castle_keyboard(),
        )


@router.callback_query(F.data == "kingdom_throne")
async def kingdom_throne_callback(callback: CallbackQuery):
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "👑 TAХT\n\n"
            "Hukmdorlik va qirollik qarorlari.",
            reply_markup=throne_keyboard(),
        )


@router.callback_query(F.data == "kingdom_army")
async def kingdom_army_callback(callback: CallbackQuery):
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "⚔️ ARMIYA\n\n"
            "Qirollik qo‘shinlarini boshqaring.",
            reply_markup=army_keyboard(),
        )


# ============================================================
# CALLBACK — INVENTORY / SHOP / CLAN / FAMILY
# ============================================================

@router.callback_query(F.data == "back_main")
async def duplicate_back_protection(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "clan_profile")
async def clan_profile_callback(callback: CallbackQuery):
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "🏴 KLAN PROFILI\n\n"
            "Klan ma’lumotlari shu yerda ko‘rsatiladi.",
            reply_markup=back_keyboard(),
        )


@router.callback_query(F.data == "family_profile")
async def family_profile_callback(callback: CallbackQuery):
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "❤️ OILA PROFILI\n\n"
            "Turmush o‘rtog‘ingiz va oilaviy ma’lumotlar.",
            reply_markup=back_keyboard(),
        )


# ============================================================
# CALLBACK — LANGUAGE
# ============================================================

@router.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: CallbackQuery):
    language = callback.data.replace("lang_", "")

    names = {
        "uz": "🇺🇿 O‘zbek tili",
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
            f"🌐 Til: {names.get(language, 'Noma’lum')}\n\n"
            "Til tizimi THRONE’ning barcha bo‘limlariga "
            "qo‘llanadi.",
            reply_markup=back_keyboard(),
        )


# ============================================================
# CALLBACK — ELITE
# ============================================================

@router.callback_query(F.data.startswith("elite_buy_"))
async def elite_purchase_callback(callback: CallbackQuery):
    period = callback.data.replace("elite_buy_", "")

    prices = {
        "7": "$1",
        "30": "$3",
        "90": "$7",
        "180": "$12",
        "365": "$20",
    }

    price = prices.get(period, "—")

    await callback.answer()

    if callback.message:
        await callback.message.answer(
            "⚜️ THRONE ELITE\n\n"
            f"📅 Muddat: {period} kun\n"
            f"💳 Narx: {price}\n\n"
            "To‘lov tasdiqlangandan so‘ng Elite avtomatik "
            "faollashtiriladi.",
            reply_markup=back_keyboard(),
        )


# ============================================================
# UNKNOWN TEXT
# ============================================================

@router.message()
async def unknown_message(message: Message):
    if message.chat.type == "private":
        await message.answer(
            "👑 THRONE\n\n"
            "Kerakli bo‘limni asosiy menyudan tanlang.",
            reply_markup=main_menu_keyboard(),
      )
