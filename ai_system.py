from dataclasses import dataclass
from typing import Optional, Dict, List

from database import get_user, get_player_stats


@dataclass
class AIResult:
    success: bool
    answer: str = ""
    category: str = "general"
    data: Optional[dict] = None


AI_CATEGORIES = {
    "general": "Umumiy yordam",
    "profile": "Profil",
    "economy": "Iqtisodiyot",
    "kingdom": "Qirollik",
    "castle": "Qal'a",
    "army": "Qo‘shin",
    "clan": "Klan",
    "family": "Oila",
    "inventory": "Inventar",
    "shop": "Do‘kon",
    "roles": "Rollar",
    "game": "O‘yin",
    "duel": "Duel",
    "tournament": "Musobaqa",
    "elite": "THRONE Elite",
    "security": "Xavfsizlik",
}


def normalize_question(question: str) -> str:
    if not question:
        return ""

    return " ".join(question.lower().strip().split())


def detect_category(question: str) -> str:
    text = normalize_question(question)

    keywords = {
        "profile": [
            "profil",
            "kabinet",
            "men haqimda",
            "darajam",
            "stats",
            "statistika",
        ],
        "economy": [
            "oltin",
            "gold",
            "coin",
            "olmos",
            "diamond",
            "pul",
            "balans",
            "hamyon",
            "transfer",
            "sovg'a",
            "sovga",
        ],
        "kingdom": [
            "qirollik",
            "kingdom",
            "qirol",
            "shoh",
            "taxt",
        ],
        "castle": [
            "qal'a",
            "qala",
            "castle",
        ],
        "army": [
            "qo'shin",
            "qoshin",
            "askar",
            "armiya",
            "army",
            "kuchlarim",
        ],
        "clan": [
            "klan",
            "clan",
            "urush",
            "clan war",
        ],
        "family": [
            "oila",
            "nikoh",
            "turmush",
            "er",
            "xotin",
            "juft",
        ],
        "inventory": [
            "inventar",
            "kiyim",
            "qurol",
            "ot",
            "buyum",
            "jihoz",
        ],
        "shop": [
            "do'kon",
            "dokon",
            "shop",
            "sotib olish",
            "narx",
            "mahsulot",
        ],
        "roles": [
            "rol",
            "rollar",
            "role",
            "vazir",
            "malika",
            "shahzoda",
            "qotil",
            "josus",
        ],
        "game": [
            "o'yin",
            "oyin",
            "newgame",
            "join",
            "start",
            "ovoz",
            "ovoz berish",
            "kecha",
            "kunduz",
        ],
        "duel": [
            "duel",
            "jang",
            "yakkama-yakka",
            "urushmoq",
        ],
        "tournament": [
            "turnir",
            "musobaqa",
            "championship",
            "cup",
        ],
        "elite": [
            "elite",
            "premium",
            "throne elite",
        ],
        "security": [
            "xavfsizlik",
            "hacker",
            "hack",
            "himoya",
            "token",
        ],
    }

    for category, words in keywords.items():
        for word in words:
            if word in text:
                return category

    return "general"


GENERAL_ANSWERS = [
    "👑 THRONE — bu strategiya, kuch va qirollik boshqaruviga asoslangan o‘yin.",
    "🏰 THRONE’da qirolligingizni rivojlantiring, kuch to‘plang va taxt uchun kurashing.",
    "⚔️ Har bir qaror THRONE olamidagi rivojlanishingizga ta'sir qiladi.",
]


CATEGORY_HELP = {
    "profile": (
        "👤 PROFIL\n\n"
        "Bu bo‘limda o‘yinchi darajasi, statistikasi, "
        "reytingi va asosiy ma'lumotlari ko‘rsatiladi."
    ),
    "economy": (
        "💰 IQTISODIYOT\n\n"
        "🟡 Oltin — asosiy valuta.\n"
        "🪙 Coin — premium ichki valuta.\n"
        "💎 Olmos — noyob premium resurs.\n\n"
        "Valutalarni do‘kon, bonus, mukofot va boshqa tizimlar orqali olish mumkin."
    ),
    "kingdom": (
        "🏰 QIROLLIK\n\n"
        "Qirolligingizni rivojlantiring, qal'ani kuchaytiring, "
        "qo‘shin tuzing va hududlarni boshqaring."
    ),
    "castle": (
        "🏰 QAL'A\n\n"
        "Qal'a darajasi oshgani sari mudofaa, xazina sig‘imi "
        "va yangi imkoniyatlar ochiladi."
    ),
    "army": (
        "⚔️ QO‘SHIN\n\n"
        "Qo‘shin qirollikning harbiy kuchidir. "
        "Askarlar, kamonchilar, otliqlar va maxsus birliklar mavjud."
    ),
    "clan": (
        "🏴 KLAN\n\n"
        "Klan yarating yoki mavjud klanga qo‘shiling. "
        "Klan darajasi, kuchi, xazinasi va klan urushlari mavjud."
    ),
    "family": (
        "❤️ OILA\n\n"
        "Nikoh Telegram guruhida taklif qilinadi. "
        "Tasdiqlangandan keyin Mini App orqali oilaviy holatni ko‘rish mumkin."
    ),
    "inventory": (
        "🎒 INVENTAR\n\n"
        "Qurol, kiyim, zirh, ot va boshqa buyumlaringiz shu yerda saqlanadi."
    ),
    "shop": (
        "💰 DO‘KON\n\n"
        "Do‘konda qurol, zirh, kiyim, ot, uzuk va maxsus buyumlarni "
        "sotib olish mumkin."
    ),
    "roles": (
        "🎭 ROLLAR\n\n"
        "THRONE guruh o‘yinida turli qirollik, qora tomon, "
        "isyon va mustaqil rollar mavjud."
    ),
    "game": (
        "🎮 O‘YIN\n\n"
        "Guruh o‘yini admin tomonidan boshlanadi.\n\n"
        "/newgame — yangi o‘yin\n"
        "/join — o‘yinga qo‘shilish\n"
        "/start — o‘yinni boshlash\n"
        "/leave — o‘yindan chiqish"
    ),
    "duel": (
        "⚔️ DUEL\n\n"
        "Ikki o‘yinchi yakkama-yakka jang qiladi. "
        "Hujum, mudofaa, sog‘liq va jihozlar natijaga ta'sir qiladi."
    ),
    "tournament": (
        "🏆 MUSOBAQALAR\n\n"
        "Solo Championship, Clan Championship va THRONE Cup "
        "kabi musobaqalar mavjud."
    ),
    "elite": (
        "⚜️ THRONE ELITE\n\n"
        "Elite — premium imkoniyatlar tizimi. "
        "Creator uchun Elite doimiy aktiv."
    ),
    "security": (
        "🛡️ XAVFSIZLIK\n\n"
        "THRONE’da maxfiy ma'lumotlar himoyalanadi. "
        "Bot tokeni va boshqa maxfiy ma'lumotlar kod ichida saqlanmaydi."
    ),
}


def get_category_help(category: str) -> str:
    return CATEGORY_HELP.get(
        category,
        "👑 THRONE AI sizga THRONE tizimlarini tushuntirishga yordam beradi.",
    )


async def get_profile_context(user_id: int) -> Dict:
    context = {
        "user_id": user_id,
        "user": None,
        "stats": None,
    }

    try:
        context["user"] = await get_user(user_id)
    except Exception:
        pass

    try:
        context["stats"] = await get_player_stats(user_id)
    except Exception:
        pass

    return context


def build_profile_answer(context: Dict) -> str:
    user = context.get("user")
    stats = context.get("stats")

    if not user:
        return "👤 Profil ma'lumotlari hali yaratilmagan."

    name = (
        user.get("first_name")
        or user.get("username")
        or "O‘yinchi"
    )

    lines = [
        f"👤 {name}",
        "",
        "👑 THRONE profili",
    ]

    if stats:
        level = stats.get("level", 1)
        wins = stats.get("wins", 0)
        losses = stats.get("losses", 0)
        games = stats.get("games_played", 0)

        lines.extend(
            [
                f"⭐ Daraja: {level}",
                f"🎮 O‘yinlar: {games}",
                f"🏆 G‘alabalar: {wins}",
                f"💀 Mag‘lubiyatlar: {losses}",
            ]
        )

    return "\n".join(lines)


def build_ai_context(user_id: int, category: str) -> Dict:
    return {
        "user_id": user_id,
        "category": category,
        "categories": list(AI_CATEGORIES.keys()),
    }


async def answer_question(
    user_id: int,
    question: str,
) -> AIResult:

    if not question or not question.strip():
        return AIResult(
            success=False,
            answer="🤖 Savolingizni yozing.",
        )

    category = detect_category(question)

    if category == "profile":
        context = await get_profile_context(user_id)

        return AIResult(
            success=True,
            answer=build_profile_answer(context),
            category=category,
            data=context,
        )

    answer = get_category_help(category)

    return AIResult(
        success=True,
        answer=answer,
        category=category,
        data=build_ai_context(user_id, category),
    )


async def ask_ai(
    user_id: int,
    question: str,
) -> str:

    result = await answer_question(
        user_id,
        question,
    )

    return result.answer


def get_ai_categories() -> List[dict]:
    return [
        {
            "key": key,
            "name": name,
        }
        for key, name in AI_CATEGORIES.items()
    ]


def get_ai_category_text() -> str:
    lines = [
        "🤖 THRONE AI",
        "",
        "Men quyidagi mavzularda yordam bera olaman:",
        "",
    ]

    for category, name in AI_CATEGORIES.items():
        lines.append(f"• {name}")

    return "\n".join(lines)


def get_ai_help() -> str:
    return (
        "🤖 THRONE AI\n\n"
        "Savolingizni oddiy tarzda yozing.\n\n"
        "Masalan:\n"
        "• Qirolligimni qanday rivojlantiraman?\n"
        "• Oltin qanday ishlaydi?\n"
        "• Klan nima?\n"
        "• Duel qanday ishlaydi?\n"
        "• Rollar qanday?\n"
        "• Elite nima?\n\n"
        "🔒 THRONE AI maxfiy rollar yoki yashirin o‘yin harakatlarini oshkor qilmaydi."
    )


def ai_can_reveal_secret_data(question: str) -> bool:
    text = normalize_question(question)

    forbidden = [
        "kimning roli",
        "kim qotil",
        "qotil kim",
        "mafia kim",
        "qora tomon kim",
        "yashirin rol",
        "maxfiy rol",
        "kim meni o'ldiradi",
        "kim meni o'ldirmoqchi",
        "secret role",
        "hidden role",
    ]

    return not any(word in text for word in forbidden)


async def secure_ai_answer(
    user_id: int,
    question: str,
) -> AIResult:

    if not ai_can_reveal_secret_data(question):
        return AIResult(
            success=False,
            category="security",
            answer=(
                "🔒 Bu ma'lumot maxfiy hisoblanadi.\n\n"
                "THRONE AI o‘yinchilarning yashirin rollari, "
                "maxfiy harakatlari yoki boshqa maxfiy ma'lumotlarni oshkor qilmaydi."
            ),
        )

    return await answer_question(
        user_id,
        question,
    )


def creator_ai_help() -> str:
    return (
        "𓆩 ELITE YARATUVCHI 𓆪\n\n"
        "🤖 THRONE AI — Creator yordam markazi.\n\n"
        "• Bot holati\n"
        "• O‘yin statistikasi\n"
        "• O‘yinchilar statistikasi\n"
        "• Reytinglar\n"
        "• Xavfsizlik holati\n"
        "• Tizimlar bo‘yicha ma'lumot\n\n"
        "⚠️ Maxfiy tokenlar va parollar AI javobida ko‘rsatilmaydi."
    )


def ai_status() -> dict:
    return {
        "enabled": True,
        "name": "THRONE AI",
        "categories": len(AI_CATEGORIES),
        "secret_data_protection": True,
        "creator_support": True,
    }


def ai_summary() -> str:
    status = ai_status()

    return (
        "🤖 THRONE AI\n\n"
        f"Holat: {'AKTIV' if status['enabled'] else 'O‘CHIQ'}\n"
        f"Bo‘limlar: {status['categories']}\n"
        "🔒 Maxfiy ma'lumot himoyasi: AKTIV\n"
        "👑 Creator yordam: AKTIV"
  )
