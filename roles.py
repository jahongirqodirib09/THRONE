from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Side(str, Enum):
    THRONE = "throne"
    SHADOW = "shadow"
    SOLO = "solo"
    SPECIAL = "special"


@dataclass(frozen=True)
class Role:
    key: str
    name: str
    side: Side
    ability: str
    ability_type: str
    uses: int | None = None
    cooldown: int = 0
    opponent: str | None = None
    win_condition: str = ""


# ============================================================
# 👑 TAHT TOMONI — 12
# ============================================================

ROLES: dict[str, Role] = {

    "shoh": Role(
        key="shoh",
        name="👑 Shoh",
        side=Side.THRONE,
        ability="Qirollik farmoni: har tun 1 o‘yinchini tanlab, uning tungi qobiliyatini bekor qiladi.",
        ability_type="block",
        uses=None,
        opponent="Soya boshlig‘i",
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "malika": Role(
        key="malika",
        name="👸 Malika",
        side=Side.THRONE,
        ability="Saroy panohi: har tun 1 o‘yinchini himoya qiladi. O‘zini himoya qila olmaydi va bir odamni ketma-ket ikki tun himoya qila olmaydi.",
        ability_type="defense",
        uses=None,
        opponent="Qotil",
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "shahzoda": Role(
        key="shahzoda",
        name="🤴 Shahzoda",
        side=Side.THRONE,
        ability="Vorislik: Shoh vafot etgach, uning ayrim vakolatlarini meros qilib oladi va keyingi oddiy tungi hujumdan bir marta omon qoladi.",
        ability_type="inheritance",
        uses=1,
        opponent="Dushman qiroli",
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "vazir": Role(
        key="vazir",
        name="🏛️ Vazir",
        side=Side.THRONE,
        ability="Saroy tekshiruvi: har tun 1 o‘yinchini tekshiradi. Natija: Taxt, Soya yoki Yakka.",
        ability_type="investigation",
        uses=None,
        opponent="Josus",
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "bosh_qomondon": Role(
        key="bosh_qomondon",
        name="⚔️ Bosh qo‘mondon",
        side=Side.THRONE,
        ability="Harbiy zarba: o‘yin davomida jami 2 marta hujum qila oladi.",
        ability_type="attack",
        uses=2,
        opponent="Dushman qo‘mondoni",
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "qirol_qoriqchisi": Role(
        key="qirol_qoriqchisi",
        name="🛡️ Qirol qo‘riqchisi",
        side=Side.THRONE,
        ability="Qalqon: har tun 1 o‘yinchini himoya qiladi. O‘zini himoya qila olmaydi, bir odamni ketma-ket ikki tun himoya qila olmaydi va Dushman suiqasdchisini to‘xtata oladi.",
        ability_type="defense",
        uses=None,
        opponent="Dushman suiqasdchisi",
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "qozi": Role(
        key="qozi",
        name="⚖️ Qozi",
        side=Side.THRONE,
        ability="Maxsus tungi huquq berilmagan. Uning asosiy kuchi muhokama, kuzatuv va oddiy ovoz berishda.",
        ability_type="passive",
        uses=None,
        opponent="Soxta maslahatchi",
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "xazinachi": Role(
        key="xazinachi",
        name="💰 Xazinachi",
        side=Side.THRONE,
        ability="Xazina muhri: har 2 tunda 1 o‘yinchini Gold/Coin kamayishi, soliq yoki jarima kabi iqtisodiy salbiy ta’sirlardan himoya qiladi. Oddiy tungi o‘limdan himoya qilmaydi.",
        ability_type="economic_defense",
        uses=None,
        cooldown=2,
        opponent="Qora Vazir",
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "qishloq_aholisi": Role(
        key="qishloq_aholisi",
        name="🏘️ Qishloq aholisi",
        side=Side.THRONE,
        ability="Maxsus tungi qobiliyat yo‘q. Asosiy kuchi — muhokama, kuzatuv va ovoz berish.",
        ability_type="passive",
        uses=None,
        opponent="Xoin",
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "xizmatkor": Role(
        key="xizmatkor",
        name="🧹 Xizmatkor",
        side=Side.THRONE,
        ability="Saroy siri: har 2 tunda 1 o‘yinchini tanlab, u harakat qilgan-qilmaganini va harakat turini biladi.",
        ability_type="observation",
        uses=None,
        cooldown=2,
        opponent=None,
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "ritsir": Role(
        key="ritsir",
        name="🏰⚔️ Ritsir",
        side=Side.THRONE,
        ability="Qo‘riqlovchi yurish: har tun 1 o‘yinchini himoya qiladi. Agar u hujumga uchrasa, Ritsir hujum bo‘lganini va Soya tomoni bilan bog‘liqligini biladi. Temir zirh birinchi oddiy tungi hujumni bir marta to‘xtatadi.",
        ability_type="defense_observation",
        uses=1,
        opponent=None,
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),

    "aygoqchi": Role(
        key="aygoqchi",
        name="🕵️ Ayg‘oqchi",
        side=Side.THRONE,
        ability="Maxfiy kuzatuv: har tun 1 o‘yinchini tekshiradi. Natija: Taxt, Soya yoki Yakka.",
        ability_type="investigation",
        uses=None,
        opponent=None,
        win_condition="Taxt tomoni bilan g‘alaba qozonish.",
    ),


    # ========================================================
    # 🕶️ SOYA TOMONI — 10
    # ========================================================

    "soya_boshligi": Role(
        key="soya_boshligi",
        name="🕶️ Soya boshlig‘i",
        side=Side.SHADOW,
        ability="Qorong‘u farmon: har tun Soya hujumining asosiy nishonini belgilaydi. Qora niqob bir marta tekshiruvda Soya tomonini yashiradi.",
        ability_type="shadow_attack_command",
        uses=1,
        opponent="Shoh",
        win_condition="Soya tomoni ustun kelishi.",
    ),

    "qotil": Role(
        key="qotil",
        name="🗡️ Qotil",
        side=Side.SHADOW,
        ability="Tungi zarba: har tun 1 nishonga oddiy hujum qiladi. Oddiy himoya uni to‘xtata oladi. Soya sherigiga hujum qila olmaydi.",
        ability_type="attack",
        uses=None,
        opponent="Malika",
        win_condition="Soya tomoni ustun kelishi.",
    ),

    "josus": Role(
        key="josus",
        name="🕵️ Josus",
        side=Side.SHADOW,
        ability="Maxfiy kuzatuv: 1 o‘yinchini tanlab, u kim bilan harakat qilganini yoki kimga borganini biladi.",
        ability_type="observation",
        uses=None,
        opponent="Vazir",
        win_condition="Soya tomoni ustun kelishi.",
    ),

    "soxta_maslahatchi": Role(
        key="soxta_maslahatchi",
        name="🎭 Soxta maslahatchi",
        side=Side.SHADOW,
        ability="Soxta iz: bir marta tekshiruv natijasini noto‘g‘ri ko‘rsatadi. Foydalanilganda o‘zini Taxt tomoni sifatida ko‘rsatishi mumkin.",
        ability_type="investigation_deception",
        uses=1,
        opponent=None,
        win_condition="Soya tomoni ustun kelishi.",
    ),

    "xoin": Role(
        key="xoin",
        name="🩸 Xoin",
        side=Side.SHADOW,
        ability="Maxsus ovoz kuchi yo‘q. Ovoz berish tizimi barcha tirik o‘yinchilar uchun teng.",
        ability_type="passive",
        uses=None,
        opponent="Qishloq aholisi",
        win_condition="Soya tomoni ustun kelishi.",
    ),

    "qora_vazir": Role(
        key="qora_vazir",
        name="🖤 Qora Vazir",
        side=Side.SHADOW,
        ability="Maxsus ovoz yoki ovozni bekor qilish vakolati yo‘q. Ovoz berish barcha tirik o‘yinchilar uchun teng.",
        ability_type="passive",
        uses=None,
        opponent="Xazinachi",
        win_condition="Soya tomoni ustun kelishi.",
    ),

    "dushman_qiroli": Role(
        key="dushman_qiroli",
        name="👑 Dushman qiroli",
        side=Side.SHADOW,
        ability="Dushman farmoni: bir marta Soya hujumini oddiy himoyadan o‘tkazishga imkon beradi. Kuchli yoki maxsus himoyalarni avtomatik ravishda chetlab o‘tmaydi.",
        ability_type="attack_bypass",
        uses=1,
        opponent="Shahzoda",
        win_condition="Soya tomoni ustun kelishi.",
    ),

    "dushman_qomondoni": Role(
        key="dushman_qomondoni",
        name="⚔️ Dushman qo‘mondoni",
        side=Side.SHADOW,
        ability="Qamal: jami 2 marta kuchli hujum qiladi. Ayrim oddiy himoyalarni chetlab o‘tadi.",
        ability_type="strong_attack",
        uses=2,
        opponent="Bosh qo‘mondon",
        win_condition="Soya tomoni ustun kelishi.",
    ),

    "dushman_josusi": Role(
        key="dushman_josusi",
        name="🕵️ Dushman josusi",
        side=Side.SHADOW,
        ability="Saroyga kirish: 1 o‘yinchini tekshiradi va unda maxsus rol bor-yo‘qligini aniqlaydi. Aniq rol yoki tomonini avtomatik ko‘rsatmaydi.",
        ability_type="role_detection",
        uses=None,
        opponent=None,
        win_condition="Soya tomoni ustun kelishi.",
    ),

    "dushman_suiqasddchisi": Role(
        key="dushman_suiqasddchisi",
        name="🗡️ Dushman suiqasdchisi",
        side=Side.SHADOW,
        ability="Suiqasd: har 2 tunda hujum qiladi. Yuqori darajadagi rollarga qarshi kuchliroq. Qirol qo‘riqchisi uni to‘xtata oladi.",
        ability_type="strong_attack",
        uses=None,
        cooldown=2,
        opponent="Qirol qo‘riqchisi",
        win_condition="Soya tomoni ustun kelishi.",
    ),


    # ========================================================
    # ⚔️ YAKKA ROLLAR — 7
    # ========================================================

    "ovchi": Role(
        key="ovchi",
        name="🐺 Ovchi",
        side=Side.SOLO,
        ability="Ov: shaxsiy nishonlarini bajarish uchun jami 2 marta hujum qila oladi.",
        ability_type="personal_attack",
        uses=2,
        opponent=None,
        win_condition="O‘zining yashirin shaxsiy g‘alaba shartini bajarish.",
    ),

    "telba": Role(
        key="telba",
        name="🃏 Telba",
        side=Side.SOLO,
        ability="Ataylab shubhali harakat qiladi. Asosiy maqsadi — kunduzgi kengash ovozi bilan chiqarib yuborilish.",
        ability_type="personal",
        uses=None,
        opponent=None,
        win_condition="Kunduzgi kengash ovozida chiqarib yuborilsa, shaxsiy g‘alaba.",
    ),

    "sayyoh": Role(
        key="sayyoh",
        name="👤 Sayyoh",
        side=Side.SOLO,
        ability="Yo‘l: har tun 1 o‘yinchiga boradi va u yerda tungi voqea bo‘lgan-bo‘lmaganini biladi.",
        ability_type="observation",
        uses=None,
        opponent=None,
        win_condition="O‘yin oxirigacha tirik qolish.",
    ),

    "yollanma_jangchi": Role(
        key="yollanma_jangchi",
        name="⚔️ Yollanma jangchi",
        side=Side.SOLO,
        ability="Shartnoma: boshqa o‘yinchi bilan vaqtinchalik kelishuv tuzadi va shartnoma vazifasini bajaradi.",
        ability_type="contract",
        uses=None,
        opponent=None,
        win_condition="Shaxsiy shartnoma vazifasini bajarish.",
    ),

    "surgun_shahzoda": Role(
        key="surgun_shahzoda",
        name="🤴 Surgun shahzoda",
        side=Side.SOLO,
        ability="Qaytish: o‘limdan bir marta o‘zini saqlab qoladi.",
        ability_type="self_save",
        uses=1,
        opponent=None,
        win_condition="Shaxsiy qaytish shartini bajarish.",
    ),

    "taxt_davogari": Role(
        key="taxt_davogari",
        name="👑 Taxt da’vogari",
        side=Side.SOLO,
        ability="Taxt talabi: yuqori martabali o‘yinchini nishonga olib, o‘zining shaxsiy taxt shartini bajarishga harakat qiladi.",
        ability_type="personal_target",
        uses=None,
        opponent=None,
        win_condition="Shaxsiy taxt da’vosi shartini bajarish.",
    ),

    "qaroqi": Role(
        key="qaroqi",
        name="🥷 Qaroqi",
        side=Side.SOLO,
        ability="Tunash: har tun 1 o‘yinchidan 200 🟡 Gold o‘g‘irlaydi. 200 yoki undan ko‘p bo‘lsa 200 oladi, 1–199 bo‘lsa hammasini oladi, 0 bo‘lsa muvaffaqiyatsiz.",
        ability_type="steal",
        uses=None,
        opponent=None,
        win_condition="Shaxsiy boylik/o‘g‘rilik shartini bajarish.",
    ),


    # ========================================================
    # ✨ MAXSUS ROLLAR — 7
    # ========================================================

    "sehrgar": Role(
        key="sehrgar",
        name="🧙 Sehrgar",
        side=Side.SPECIAL,
        ability="Sehr: cheklangan marta tungi qobiliyatni bloklash yoki o‘zgartirishga urinadi.",
        ability_type="magic",
        uses=2,
        opponent=None,
        win_condition="Yashirin shaxsiy g‘alaba shartini bajarish.",
    ),

    "tabib": Role(
        key="tabib",
        name="🩺 Tabib",
        side=Side.SPECIAL,
        ability="Davolash: har tun 1 o‘yinchini tungi o‘limdan saqlashga urinadi. Bir odamni ketma-ket ikki tun davolay olmaydi.",
        ability_type="healing",
        uses=None,
        opponent=None,
        win_condition="Belgilangan shaxs yoki tomon uchun shaxsiy vazifani bajarish.",
    ),

    "kuzatuvchi": Role(
        key="kuzatuvchi",
        name="👁️ Kuzatuvchi",
        side=Side.SPECIAL,
        ability="Kuzatuv: tanlangan o‘yinchiga tunda kimlar tashrif buyurganini ko‘radi.",
        ability_type="observation",
        uses=None,
        opponent=None,
        win_condition="Shaxsiy kuzatuv vazifasini bajarish.",
    ),

    "qorovul": Role(
        key="qorovul",
        name="🔒 Qorovul",
        side=Side.SPECIAL,
        ability="Darvoza: tanlangan o‘yinchini ayrim yashirin tungi harakatlardan himoya qiladi. Ba’zi kuchli maxsus qobiliyatlar uni chetlab o‘tishi mumkin.",
        ability_type="block_defense",
        uses=None,
        opponent=None,
        win_condition="Tanlangan o‘yinchini himoya qilish bo‘yicha shaxsiy vazifani bajarish.",
    ),

    "solnomachi": Role(
        key="solnomachi",
        name="📜 Solnomachi",
        side=Side.SPECIAL,
        ability="Xotira: oldingi tunlardan 1 muhim voqea haqida cheklangan ma’lumot oladi.",
        ability_type="history",
        uses=None,
        opponent=None,
        win_condition="Shaxsiy ma’lumot vazifasini bajarish.",
    ),

    "savdogar": Role(
        key="savdogar",
        name="💰 Savdogar",
        side=Side.SPECIAL,
        ability="Savdo: kunduz kuni boshqa o‘yinchilar bilan resurs yoki buyumlarni almashtiradi.",
        ability_type="trade",
        uses=None,
        opponent=None,
        win_condition="Shaxsiy savdo/resurs shartini bajarish.",
    ),

    "suiqasddchi": Role(
        key="suiqasddchi",
        name="🗡️ Suiqasdchi",
        side=Side.SPECIAL,
        ability="Yashirin pichoq: cheklangan marta yashirin hujum qiladi. Hujum manbasi darhol oshkor qilinmaydi.",
        ability_type="hidden_attack",
        uses=2,
        opponent="Qirol qo‘riqchisi",
        win_condition="Belgilangan shaxsiy nishonni bajarish.",
    ),
}


# ============================================================
# YORDAMCHI FUNKSIYALAR
# ============================================================

def get_role(role_key: str) -> Role | None:
    """Rol kaliti orqali rolni olish."""
    return ROLES.get(role_key)


def all_roles() -> list[Role]:
    """Barcha 36 rolni qaytaradi."""
    return list(ROLES.values())


def roles_by_side(side: Side) -> list[Role]:
    """Berilgan tomon rollarini qaytaradi."""
    return [
        role
        for role in ROLES.values()
        if role.side == side
    ]


def role_count() -> int:
    """Umumiy rol soni."""
    return len(ROLES)


def is_valid_role(role_key: str) -> bool:
    """Rol mavjudligini tekshiradi."""
    return role_key in ROLES


def get_role_side(role_key: str) -> Side | None:
    """Rol tomonini qaytaradi."""
    role = get_role(role_key)
    return role.side if role else None


def get_role_name(role_key: str) -> str:
    """Rolning ko‘rinadigan nomini qaytaradi."""
    role = get_role(role_key)
    return role.name if role else "Noma’lum rol"


def get_role_keys() -> list[str]:
    """Barcha rol kalitlarini qaytaradi."""
    return list(ROLES.keys())


# ============================================================
# KELISHILGAN OVOZ QOIDASI
# ============================================================

VOTING_RULES = {
    "one_vote_per_alive_player": True,
    "roles_modify_votes": False,
    "roles_cancel_votes": False,
    "roles_break_ties": False,
    "tie_eliminates_no_one": True,
    "dead_players_can_vote": False,
}
