# ============================================================
# THRONE — 35 ROLES
# ============================================================

SIDE_TAXT = "Taxt"
SIDE_QORA = "Qora"
SIDE_ISYON = "Isyon"
SIDE_MUSTAQIL = "Mustaqil"


ROLES = {

    # ========================================================
    # 👑 TAXT — 17
    # ========================================================

    "king": {
        "name": "👑 Shoh",
        "side": SIDE_TAXT,
        "description": "Qirollikning oliy hukmdori.",
        "ability": "Qirollikning asosiy siyosiy markazi.",
        "limitation": "Shohning yo‘q qilinishi Taxt tomoniga katta zarba beradi.",
        "win": "Qora va Isyon kuchlarini mag‘lub etish.",
    },

    "queen": {
        "name": "👸 Malika",
        "side": SIDE_TAXT,
        "description": "Saroyning siyosiy va ijtimoiy vakili.",
        "ability": "Ittifoqlar va saroy ta’siridan foydalanadi.",
        "limitation": "Mustaqil hujum kuchi cheklangan.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "minister": {
        "name": "🏛️ Vazir",
        "side": SIDE_TAXT,
        "description": "Shohning bosh maslahatchisi.",
        "ability": "Siyosiy qarorlarga ta’sir ko‘rsatadi.",
        "limitation": "Haqiqiy tomonini yashirish zarur.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "prince": {
        "name": "🤴 Shahzoda",
        "side": SIDE_TAXT,
        "description": "Qirollik taxtining vorisi.",
        "ability": "Maxsus himoya va vorislik maqomiga ega.",
        "limitation": "Ochiq nishonga aylanishi mumkin.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "commander": {
        "name": "⚔️ Bosh qo‘mondon",
        "side": SIDE_TAXT,
        "description": "Qirollik qo‘shinlarining boshqaruvchisi.",
        "ability": "Harbiy kuchga strategik bonus beradi.",
        "limitation": "Siyosiy tekshiruvlardan himoyalanmagan.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "royal_guard": {
        "name": "🛡️ Qirol qo‘riqchisi",
        "side": SIDE_TAXT,
        "description": "Saroydagi eng ishonchli himoyachilardan biri.",
        "ability": "Tanlangan o‘yinchini himoya qiladi.",
        "limitation": "Bir vaqtning o‘zida cheklangan himoya.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "judge": {
        "name": "⚖️ Qozi",
        "side": SIDE_TAXT,
        "description": "Qirollikdagi hukm va ovoz jarayonlarini nazorat qiladi.",
        "ability": "Ovoz berish jarayoniga ta’sir ko‘rsatishi mumkin.",
        "limitation": "Qobiliyatlari foydalanish shartlariga bog‘liq.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "treasurer": {
        "name": "💰 Xazinachi",
        "side": SIDE_TAXT,
        "description": "Qirollik xazinasini boshqaradi.",
        "ability": "Iqtisodiy bonuslar beradi.",
        "limitation": "To‘g‘ridan-to‘g‘ri jangovar kuchi past.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "doctor": {
        "name": "🩺 Tabib",
        "side": SIDE_TAXT,
        "description": "Qirollik shifokori.",
        "ability": "Tanlangan o‘yinchini hujumdan himoya qiladi.",
        "limitation": "Himoya imkoniyati cheklangan.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "spy": {
        "name": "🕵️ Josus",
        "side": SIDE_TAXT,
        "description": "Yashirin ma’lumotlarni izlaydi.",
        "ability": "Tanlangan o‘yinchi haqida yashirin ma’lumot oladi.",
        "limitation": "Noto‘g‘ri xulosa qilish xavfi mavjud.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "astrologer": {
        "name": "🔮 Munajjim",
        "side": SIDE_TAXT,
        "description": "Sirli belgilar orqali tomonlarni aniqlaydi.",
        "ability": "Tanlangan o‘yinchining tomonini tekshiradi.",
        "limitation": "Tekshiruvlar soni cheklangan.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "palace_guard": {
        "name": "🗡️ Saroy qo‘riqchisi",
        "side": SIDE_TAXT,
        "description": "Saroy xavfsizligini ta’minlaydi.",
        "ability": "Hujum qilingan paytda qarshi hujum qilishi mumkin.",
        "limitation": "Qarshi hujum imkoniyati cheklangan.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "falconer": {
        "name": "🦅 Qushboqar",
        "side": SIDE_TAXT,
        "description": "Qirollikning kuzatuvchisi.",
        "ability": "Yashirin harakatlar haqida ma’lumot yig‘adi.",
        "limitation": "To‘g‘ridan-to‘g‘ri hujum qila olmaydi.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "scribe": {
        "name": "📜 Kotib",
        "side": SIDE_TAXT,
        "description": "Qirollik voqealarini qayd etadi.",
        "ability": "Ayrim o‘yin voqealarini aniqlashtirish imkoniga ega.",
        "limitation": "Jangovar kuchga ega emas.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "hunter": {
        "name": "🏹 Ovchi",
        "side": SIDE_TAXT,
        "description": "Qirollikning mohir mergani.",
        "ability": "Bir martalik qarshi hujum amalga oshirishi mumkin.",
        "limitation": "Maxsus hujum imkoniyati bir martalik.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "guide": {
        "name": "🧭 Yo‘lchi",
        "side": SIDE_TAXT,
        "description": "Yashirin harakatlarni kuzatadi.",
        "ability": "Tanlangan o‘yinchining harakat yo‘nalishini tekshiradi.",
        "limitation": "Aniq rolni har doim aniqlay olmaydi.",
        "win": "Taxt tomonining g‘alabasi.",
    },

    "herald": {
        "name": "🔔 Jar soluvchi",
        "side": SIDE_TAXT,
        "description": "Qirollik xabarlarini xalqqa yetkazadi.",
        "ability": "Kunlik ovoz yoki sud jarayoniga ta’sir qilishi mumkin.",
        "limitation": "Qobiliyati shartlarga bog‘liq.",
        "win": "Taxt tomonining g‘alabasi.",
    },


    # ========================================================
    # 🩸 QORA — 8
    # ========================================================

    "dark_lord": {
        "name": "🩸 Qora hukmdor",
        "side": SIDE_QORA,
        "description": "Qora tomonning yashirin rahbari.",
        "ability": "Qora kuchlarni boshqaradi.",
        "limitation": "Aniqlansa, butun Qora tomon xavf ostida qoladi.",
        "win": "Qora tomon ustunlikka erishishi.",
    },

    "assassin": {
        "name": "🗡️ Qotil",
        "side": SIDE_QORA,
        "description": "Yashirin hujumchi.",
        "ability": "Tanlangan nishonga hujum qiladi.",
        "limitation": "Nishonni ehtiyotkorlik bilan tanlashi kerak.",
        "win": "Qora tomon g‘alabasi.",
    },

    "poisoner": {
        "name": "🕷️ Zaharsoch",
        "side": SIDE_QORA,
        "description": "Yashirin zaharlovchi.",
        "ability": "Nishonni zaharlab, vaqt o‘tishi bilan zaiflashtiradi.",
        "limitation": "Ta’siri darhol yakunlanmasligi mumkin.",
        "win": "Qora tomon g‘alabasi.",
    },

    "shadow": {
        "name": "🕶️ Soya",
        "side": SIDE_QORA,
        "description": "Tekshiruvlardan yashirinishga ixtisoslashgan.",
        "ability": "Ayrim tekshiruvlarda o‘zini yashirishi mumkin.",
        "limitation": "To‘g‘ridan-to‘g‘ri kuchi past.",
        "win": "Qora tomon g‘alabasi.",
    },

    "burner": {
        "name": "🔥 Yondiruvchi",
        "side": SIDE_QORA,
        "description": "Uzoq muddatli xavf yaratadi.",
        "ability": "Nishonga davomiy zarar yoki zaiflashtiruvchi ta’sir beradi.",
        "limitation": "Ta’siri vaqt talab qiladi.",
        "win": "Qora tomon g‘alabasi.",
    },

    "trapper": {
        "name": "🪤 Tuzoqchi",
        "side": SIDE_QORA,
        "description": "Yashirin tuzoqlar o‘rnatadi.",
        "ability": "Tanlangan o‘yinchining harakatini cheklashi mumkin.",
        "limitation": "Tuzoq imkoniyatlari cheklangan.",
        "win": "Qora tomon g‘alabasi.",
    },

    "master_poisoner": {
        "name": "🧪 Zahar ustasi",
        "side": SIDE_QORA,
        "description": "Qora tomonning eng kuchli zahar mutaxassislaridan biri.",
        "ability": "Kuchli zahar yoki zaiflashtirish ta’siridan foydalanadi.",
        "limitation": "Maxsus qobiliyati cheklangan.",
        "win": "Qora tomon g‘alabasi.",
    },

    "dark_hunter": {
        "name": "🐺 Qora ovchi",
        "side": SIDE_QORA,
        "description": "Zaiflashgan nishonlarni ovlaydi.",
        "ability": "Zaif yoki jarohatlangan nishonlarga kuchliroq hujum qiladi.",
        "limitation": "To‘liq kuchdagi nishonga qarshi samarasi pastroq.",
        "win": "Qora tomon g‘alabasi.",
    },


    # ========================================================
    # ⚔️ ISYON — 6
    # ========================================================

    "rebel_leader": {
        "name": "⚔️ Isyonchi boshlig‘i",
        "side": SIDE_ISYON,
        "description": "Taxtga qarshi chiqqan isyonchilar rahbari.",
        "ability": "Isyon kuchlarini boshqaradi.",
        "limitation": "Taxt va Qora tomonlari tomonidan nishonga olinadi.",
        "win": "Isyon tomonining g‘alabasi.",
    },

    "executioner": {
        "name": "🪓 Jallod",
        "side": SIDE_ISYON,
        "description": "Zaiflashgan dushmanlarni yo‘q qiladi.",
        "ability": "Zaif nishonga kuchli hujum qiladi.",
        "limitation": "Kuchli nishonga samarasi pastroq.",
        "win": "Isyon tomonining g‘alabasi.",
    },

    "rebel": {
        "name": "🏴 Isyonchi",
        "side": SIDE_ISYON,
        "description": "Qirollik tuzumiga qarshi oddiy isyonchi.",
        "ability": "Isyonchilar jamoasida strategik harakat qiladi.",
        "limitation": "Maxsus qobiliyati cheklangan.",
        "win": "Isyon tomonining g‘alabasi.",
    },

    "schemer": {
        "name": "🐍 Fitnachi",
        "side": SIDE_ISYON,
        "description": "Odamlar orasida shubha va nizolar yaratadi.",
        "ability": "Ovoz va qaror jarayoniga ta’sir ko‘rsatishi mumkin.",
        "limitation": "To‘g‘ridan-to‘g‘ri jangovar kuchi past.",
        "win": "Isyon tomonining g‘alabasi.",
    },

    "false_advisor": {
        "name": "🕯️ Soxta maslahatchi",
        "side": SIDE_ISYON,
        "description": "Yolg‘on ma’lumotlar orqali boshqalarni chalg‘itadi.",
        "ability": "Noto‘g‘ri ma’lumot yoki shubha tarqatishi mumkin.",
        "limitation": "Ta’siri boshqa o‘yinchilarning qarorlariga bog‘liq.",
        "win": "Isyon tomonining g‘alabasi.",
    },

    "avenger": {
        "name": "🦂 Qasoskor",
        "side": SIDE_ISYON,
        "description": "Yo‘q qilingan ittifoqchilar uchun qasos oladi.",
        "ability": "Eliminatsiyadan keyin maxsus qasos imkoniga ega.",
        "limitation": "Qasos mexanizmi cheklangan.",
        "win": "Isyon tomonining g‘alabasi.",
    },


    # ========================================================
    # ☠️ MUSTAQIL — 4
    # ========================================================

    "madman": {
        "name": "🃏 Telba",
        "side": SIDE_MUSTAQIL,
        "description": "O‘zining alohida maqsadiga ega.",
        "ability": "O‘zini ovoz orqali chiqarib yuborishga harakat qiladi.",
        "limitation": "Oddiy tomonlarning g‘alabasi unga tegishli emas.",
        "win": "Ovoz berish orqali chiqarib yuborilsa, maxsus g‘alaba.",
    },

    "revenant": {
        "name": "💀 Qasoskor ruh",
        "side": SIDE_MUSTAQIL,
        "description": "Yo‘q qilinganidan keyin ham cheklangan ta’sirga ega.",
        "ability": "O‘limdan keyin maxsus cheklangan ta’sir ko‘rsatadi.",
        "limitation": "Tirik o‘yinchilar kabi harakat qila olmaydi.",
        "win": "O‘zining maxsus shartini bajarish.",
    },

    "lone_hunter": {
        "name": "🐺 Yolg‘iz ovchi",
        "side": SIDE_MUSTAQIL,
        "description": "Hech bir tomon bilan to‘liq ittifoq qilmaydi.",
        "ability": "Tirik qolgan dushmanlarni yakka tartibda ovlaydi.",
        "limitation": "Yordamchi jamoasi yo‘q.",
        "win": "Maxsus yakka g‘alaba shartini bajarish.",
    },

    "shadow_king": {
        "name": "👤 Soyadagi qirol",
        "side": SIDE_MUSTAQIL,
        "description": "Haqiqiy maqsadini yashirgan sirli hukmdor.",
        "ability": "Yashirin maxsus maqsad asosida harakat qiladi.",
        "limitation": "G‘alaba sharti oddiy tomonlardan farq qiladi.",
        "win": "Maxsus yashirin maqsadni bajarish.",
    },
}


# ============================================================
# HELPERS
# ============================================================

def get_role(role_key: str):
    return ROLES.get(role_key)


def get_all_roles():
    return ROLES


def get_roles_by_side(side: str):
    return {
        key: role
        for key, role in ROLES.items()
        if role.get("side") == side
    }


def role_count() -> int:
    return len(ROLES)


def get_role_name(role_key: str) -> str:
    role = ROLES.get(role_key)

    if not role:
        return role_key

    return role.get("name", role_key)


def get_role_description(role_key: str) -> str:
    role = ROLES.get(role_key)

    if not role:
        return ""

    return role.get("description", "")


def get_role_ability(role_key: str) -> str:
    role = ROLES.get(role_key)

    if not role:
        return ""

    return role.get("ability", "")


def get_role_win_condition(role_key: str) -> str:
    role = ROLES.get(role_key)

    if not role:
        return ""

    return role.get("win", "")


def is_valid_role(role_key: str) -> bool:
    return role_key in ROLES
