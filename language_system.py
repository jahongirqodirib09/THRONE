from dataclasses import dataclass
from typing import Dict, List, Optional

from database import get_user


LANG_UZ = "uz"
LANG_RU = "ru"
LANG_EN = "en"
LANG_TR = "tr"
LANG_AR = "ar"
LANG_KY = "ky"

SUPPORTED_LANGUAGES = {
    LANG_UZ: {
        "name": "O‘zbekcha",
        "flag": "🇺🇿",
    },
    LANG_RU: {
        "name": "Русский",
        "flag": "🇷🇺",
    },
    LANG_EN: {
        "name": "English",
        "flag": "🇬🇧",
    },
    LANG_TR: {
        "name": "Türkçe",
        "flag": "🇹🇷",
    },
    LANG_AR: {
        "name": "العربية",
        "flag": "🇸🇦",
    },
    LANG_KY: {
        "name": "Кыргызча",
        "flag": "🇰🇬",
    },
}

DEFAULT_LANGUAGE = LANG_UZ


@dataclass
class LanguageResult:
    success: bool
    language: str = DEFAULT_LANGUAGE
    message: str = ""
    data: Optional[dict] = None


def is_supported_language(language: str) -> bool:
    return language in SUPPORTED_LANGUAGES


def get_supported_languages() -> Dict[str, dict]:
    return SUPPORTED_LANGUAGES.copy()


def get_language_name(language: str) -> str:
    language_data = SUPPORTED_LANGUAGES.get(language)

    if not language_data:
        return SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]["name"]

    return language_data["name"]


def get_language_flag(language: str) -> str:
    language_data = SUPPORTED_LANGUAGES.get(language)

    if not language_data:
        return SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]["flag"]

    return language_data["flag"]


def get_language_label(language: str) -> str:
    return f"{get_language_flag(language)} {get_language_name(language)}"


async def get_user_language(user_id: int) -> str:
    try:
        user = await get_user(user_id)

        if user:
            language = user.get("language")

            if language and is_supported_language(language):
                return language

    except Exception:
        pass

    return DEFAULT_LANGUAGE


async def set_user_language(
    user_id: int,
    language: str,
) -> LanguageResult:

    if not is_supported_language(language):
        return LanguageResult(
            success=False,
            language=DEFAULT_LANGUAGE,
            message="Qo‘llab-quvvatlanmaydigan til.",
        )

    try:
        from database import execute

        await execute(
            """
            UPDATE users
            SET language = ?
            WHERE user_id = ?
            """,
            (language, user_id),
        )

        return LanguageResult(
            success=True,
            language=language,
            message=get_language_label(language),
        )

    except Exception as exc:
        return LanguageResult(
            success=False,
            language=DEFAULT_LANGUAGE,
            message=f"Tilni saqlashda xatolik: {exc}",
        )


LANGUAGE_TEXTS = {
    LANG_UZ: {
        "welcome": "👑 THRONE’ga xush kelibsiz, {name}!",
        "cabinet": "👤 KABINET",
        "kingdom": "🏰 QIROLLIGIM",
        "inventory": "🎒 INVENTAR",
        "shop": "💰 DO‘KON",
        "clan": "🏴 KLANIM",
        "family": "❤️ OILA",
        "army": "⚔️ KUCHLARIM",
        "tournaments": "🏆 MUSOBAQALAR",
        "roles": "🎭 ROLLAR",
        "ranking": "📊 REYTING",
        "rewards": "🎁 BONUSLAR",
        "black_market": "🕶️ QORA BOZOR",
        "elite": "⚜️ THRONE ELITE",
        "language": "🌐 TIL",
        "ai": "🤖 THRONE AI",
        "help": "❓ YORDAM",
        "settings": "⚙️ SOZLAMALAR",
        "back": "🔙 ORTGA",
        "language_changed": "🌐 Til muvaffaqiyatli o‘zgartirildi.",
        "choose_language": "🌐 Tilni tanlang:",
        "language_settings": "🌐 Til sozlamalari",
        "not_found": "Ma’lumot topilmadi.",
        "yes": "Ha",
        "no": "Yo‘q",
        "close": "Yopish",
        "loading": "⏳ Yuklanmoqda...",
        "error": "❌ Xatolik yuz berdi.",
    },

    LANG_RU: {
        "welcome": "👑 Добро пожаловать в THRONE, {name}!",
        "cabinet": "👤 КАБИНЕТ",
        "kingdom": "🏰 МОЁ КОРОЛЕВСТВО",
        "inventory": "🎒 ИНВЕНТАРЬ",
        "shop": "💰 МАГАЗИН",
        "clan": "🏴 МОЙ КЛАН",
        "family": "❤️ СЕМЬЯ",
        "army": "⚔️ МОИ СИЛЫ",
        "tournaments": "🏆 ТУРНИРЫ",
        "roles": "🎭 РОЛИ",
        "ranking": "📊 РЕЙТИНГ",
        "rewards": "🎁 НАГРАДЫ",
        "black_market": "🕶️ ЧЁРНЫЙ РЫНОК",
        "elite": "⚜️ THRONE ELITE",
        "language": "🌐 ЯЗЫК",
        "ai": "🤖 THRONE AI",
        "help": "❓ ПОМОЩЬ",
        "settings": "⚙️ НАСТРОЙКИ",
        "back": "🔙 НАЗАД",
        "language_changed": "🌐 Язык успешно изменён.",
        "choose_language": "🌐 Выберите язык:",
        "language_settings": "🌐 Настройки языка",
        "not_found": "Информация не найдена.",
        "yes": "Да",
        "no": "Нет",
        "close": "Закрыть",
        "loading": "⏳ Загрузка...",
        "error": "❌ Произошла ошибка.",
    },

    LANG_EN: {
        "welcome": "👑 Welcome to THRONE, {name}!",
        "cabinet": "👤 CABINET",
        "kingdom": "🏰 MY KINGDOM",
        "inventory": "🎒 INVENTORY",
        "shop": "💰 SHOP",
        "clan": "🏴 MY CLAN",
        "family": "❤️ FAMILY",
        "army": "⚔️ MY FORCES",
        "tournaments": "🏆 TOURNAMENTS",
        "roles": "🎭 ROLES",
        "ranking": "📊 RANKING",
        "rewards": "🎁 REWARDS",
        "black_market": "🕶️ BLACK MARKET",
        "elite": "⚜️ THRONE ELITE",
        "language": "🌐 LANGUAGE",
        "ai": "🤖 THRONE AI",
        "help": "❓ HELP",
        "settings": "⚙️ SETTINGS",
        "back": "🔙 BACK",
        "language_changed": "🌐 Language changed successfully.",
        "choose_language": "🌐 Choose your language:",
        "language_settings": "🌐 Language settings",
        "not_found": "Information not found.",
        "yes": "Yes",
        "no": "No",
        "close": "Close",
        "loading": "⏳ Loading...",
        "error": "❌ An error occurred.",
    },

    LANG_TR: {
        "welcome": "👑 THRONE’a hoş geldiniz, {name}!",
        "cabinet": "👤 KABİN",
        "kingdom": "🏰 KRALLIĞIM",
        "inventory": "🎒 ENVANTER",
        "shop": "💰 MAĞAZA",
        "clan": "🏴 KLANIM",
        "family": "❤️ AİLE",
        "army": "⚔️ GÜÇLERİM",
        "tournaments": "🏆 TURNUVALAR",
        "roles": "🎭 ROLLER",
        "ranking": "📊 SIRALAMA",
        "rewards": "🎁 ÖDÜLLER",
        "black_market": "🕶️ KARABORSA",
        "elite": "⚜️ THRONE ELITE",
        "language": "🌐 DİL",
        "ai": "🤖 THRONE AI",
        "help": "❓ YARDIM",
        "settings": "⚙️ AYARLAR",
        "back": "🔙 GERİ",
        "language_changed": "🌐 Dil başarıyla değiştirildi.",
        "choose_language": "🌐 Dilinizi seçin:",
        "language_settings": "🌐 Dil ayarları",
        "not_found": "Bilgi bulunamadı.",
        "yes": "Evet",
        "no": "Hayır",
        "close": "Kapat",
        "loading": "⏳ Yükleniyor...",
        "error": "❌ Bir hata oluştu.",
    },

    LANG_AR: {
        "welcome": "👑 مرحباً بك في THRONE، {name}!",
        "cabinet": "👤 الملف الشخصي",
        "kingdom": "🏰 مملكتي",
        "inventory": "🎒 الحقيبة",
        "shop": "💰 المتجر",
        "clan": "🏴 عشيرتي",
        "family": "❤️ العائلة",
        "army": "⚔️ قواتي",
        "tournaments": "🏆 البطولات",
        "roles": "🎭 الأدوار",
        "ranking": "📊 التصنيف",
        "rewards": "🎁 المكافآت",
        "black_market": "🕶️ السوق السوداء",
        "elite": "⚜️ THRONE ELITE",
        "language": "🌐 اللغة",
        "ai": "🤖 THRONE AI",
        "help": "❓ المساعدة",
        "settings": "⚙️ الإعدادات",
        "back": "🔙 رجوع",
        "language_changed": "🌐 تم تغيير اللغة بنجاح.",
        "choose_language": "🌐 اختر لغتك:",
        "language_settings": "🌐 إعدادات اللغة",
        "not_found": "لم يتم العثور على المعلومات.",
        "yes": "نعم",
        "no": "لا",
        "close": "إغلاق",
        "loading": "⏳ جارٍ التحميل...",
        "error": "❌ حدث خطأ.",
    },

    LANG_KY: {
        "welcome": "👑 THRONE’го кош келиңиз, {name}!",
        "cabinet": "👤 КАБИНЕТ",
        "kingdom": "🏰 МЕНИН ПАДЫШАЛЫГЫМ",
        "inventory": "🎒 ИНВЕНТАРЬ",
        "shop": "💰 ДҮКӨН",
        "clan": "🏴 МЕНИН КЛАНЫМ",
        "family": "❤️ ҮЙ-БҮЛӨ",
        "army": "⚔️ МЕНИН КҮЧТӨРҮМ",
        "tournaments": "🏆 ТУРНИРЛЕР",
        "roles": "🎭 РОЛДОР",
        "ranking": "📊 РЕЙТИНГ",
        "rewards": "🎁 СЫЙЛЫКТАР",
        "black_market": "🕶️ КАРА БАЗАР",
        "elite": "⚜️ THRONE ELITE",
        "language": "🌐 ТИЛ",
        "ai": "🤖 THRONE AI",
        "help": "❓ ЖАРДАМ",
        "settings": "⚙️ ЖӨНДӨӨЛӨР",
        "back": "🔙 АРТКА",
        "language_changed": "🌐 Тил ийгиликтүү өзгөртүлдү.",
        "choose_language": "🌐 Тилди тандаңыз:",
        "language_settings": "🌐 Тил жөндөөлөрү",
        "not_found": "Маалымат табылган жок.",
        "yes": "Ооба",
        "no": "Жок",
        "close": "Жабуу",
        "loading": "⏳ Жүктөлүүдө...",
        "error": "❌ Ката кетти.",
    },
}


def translate(
    language: str,
    key: str,
    **kwargs,
) -> str:

    if not is_supported_language(language):
        language = DEFAULT_LANGUAGE

    language_data = LANGUAGE_TEXTS.get(
        language,
        LANGUAGE_TEXTS[DEFAULT_LANGUAGE],
    )

    text = language_data.get(
        key,
        LANGUAGE_TEXTS[DEFAULT_LANGUAGE].get(key, key),
    )

    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text


async def t(
    user_id: int,
    key: str,
    **kwargs,
) -> str:

    language = await get_user_language(user_id)

    return translate(
        language,
        key,
        **kwargs,
    )


def get_language_keyboard_data() -> List[dict]:
    result = []

    for code, data in SUPPORTED_LANGUAGES.items():
        result.append(
            {
                "code": code,
                "name": data["name"],
                "flag": data["flag"],
                "label": f"{data['flag']} {data['name']}",
            }
        )

    return result


def language_summary(language: str) -> dict:
    if not is_supported_language(language):
        language = DEFAULT_LANGUAGE

    return {
        "code": language,
        "name": get_language_name(language),
        "flag": get_language_flag(language),
        "label": get_language_label(language),
    }


def get_all_translation_keys() -> List[str]:
    keys = set()

    for language_data in LANGUAGE_TEXTS.values():
        keys.update(language_data.keys())

    return sorted(keys)


def validate_translation_keys() -> dict:
    base_keys = set(
        LANGUAGE_TEXTS[DEFAULT_LANGUAGE].keys()
    )

    result = {}

    for language, texts in LANGUAGE_TEXTS.items():
        current_keys = set(texts.keys())

        result[language] = {
            "missing": sorted(base_keys - current_keys),
            "extra": sorted(current_keys - base_keys),
            "complete": base_keys.issubset(current_keys),
        }

    return result


def get_language_statistics() -> dict:
    validation = validate_translation_keys()

    return {
        "supported_languages": len(SUPPORTED_LANGUAGES),
        "language_codes": list(SUPPORTED_LANGUAGES.keys()),
        "translation_keys": len(
            get_all_translation_keys()
        ),
        "validation": validation,
}
