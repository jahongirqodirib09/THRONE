# roles.py
# THRONE — Taxtlar O‘yini
# 36 ta asosiy rol

ROLES = [
    # =========================
    # 👑 KRON — 12
    # =========================
    ("shoh", "👑 Shoh", "KRON", "Qirollikning markaziy figurasi."),
    ("malika", "👸 Malika", "KRON", "Qirollikdagi yuqori martabali himoya/siyosiy rol."),
    ("shahzoda", "🤴 Shahzoda", "KRON", "Shohning vorisi."),
    ("vazir", "🏛️ Vazir", "KRON", "Shohga yaqin siyosiy rol."),
    ("bosh_qomondon", "⚔️ Bosh qo‘mondon", "KRON", "Qirollik harbiy kuchlarining boshlig‘i."),
    ("qirol_qoriqchisi", "🛡️ Qirol qo‘riqchisi", "KRON", "Muhim shaxslarni himoya qiladi."),
    ("qozi", "⚖️ Qozi", "KRON", "Sud va ovoz berish bilan bog‘liq maxsus rol."),
    ("xazinachi", "💰 Xazinachi", "KRON", "Qirollik xazinasi bilan bog‘liq rol."),
    ("ritsar", "🏰 Ritsir", "KRON", "Jangovar himoya roli."),
    ("xizmatkor", "🧹 Xizmatkor", "KRON", "Yashirin imkoniyatga ega bo‘lishi mumkin."),
    ("tinch_aholi", "🏘️ Tinch aholi", "KRON", "Oddiy qirollik fuqarosi."),
    ("aygoqchi", "🕵️ Ayg‘oqchi", "KRON", "Dushman haqida ma’lumot yig‘adi."),

    # =========================
    # 🦅 SOYA — 10
    # =========================
    ("soya_boshligi", "🦅 Soya boshlig‘i", "SOYA", "Soya kuchlarining asosiy rahbari."),
    ("qotil", "🗡️ Qotil", "SOYA", "Tungi hujumlarning asosiy ijrochisi."),
    ("josus", "🕵️ Josus", "SOYA", "Qirollik ichiga kirib, ma’lumot yig‘adi."),
    ("soxta_maslahatchi", "🎭 Soxta maslahatchi", "SOYA", "O‘zini KRON tarafdori qilib ko‘rsatishi mumkin."),
    ("xoin", "🩸 Xoin", "SOYA", "Qirollik ichidagi yashirin dushman."),
    ("qora_vazir", "🖤 Qora vazir", "SOYA", "Siyosiy manipulyatsiyaga ixtisoslashgan."),
    ("dushman_qiroli", "👑 Dushman qiroli", "SOYA", "Soya kuchlarining yuqori hokimiyat figurasi."),
    ("dushman_qomondoni", "⚔️ Dushman qo‘mondoni", "SOYA", "Kuchli harbiy dushman."),
    ("dushman_josusi", "🕵️ Dushman josusi", "SOYA", "Kuzatuv va ma’lumot yig‘ishga ixtisoslashgan."),
    ("dushman_suiqasdchisi", "🗡️ Dushman suiqasdchisi", "SOYA", "Kuchli yashirin suiqasdga ega."),

    # =========================
    # 🐺 YAKKA — 7
    # =========================
    ("ovchi", "🐺 Ovchi", "YAKKA", "O‘zining alohida maqsadiga ega."),
    ("telba", "🃏 Telba", "YAKKA", "Maxsus g‘alaba shartiga ega."),
    ("sayyoh", "👤 Sayyoh", "YAKKA", "Qirollik siyosatiga bevosita bog‘lanmagan."),
    ("yollanma_jangchi", "⚔️ Yollanma jangchi", "YAKKA", "Vaziyatga qarab ittifoq qilishi mumkin."),
    ("surgun_shahzoda", "🤴 Surgun shahzoda", "YAKKA", "Alohida qaytish/g‘alaba yo‘liga ega."),
    ("taxt_davogari", "👑 Taxt da’vogari", "YAKKA", "Taxtni egallashga urinadi."),
    ("qaroqchi", "🥷 Qaroqchi", "YAKKA", "Yashirin harakat va resurslar bilan bog‘liq."),

    # =========================
    # 🛡️ LEGION — 7
    # =========================
    ("tabib", "🩺 Tabib", "LEGION", "Jarohatlangan o‘yinchilarga yordam beradi."),
    ("kuzatuvchi", "👁️ Kuzatuvchi", "LEGION", "Boshqa o‘yinchilarning harakatlarini kuzatadi."),
    ("qorovul", "🔒 Qorovul", "LEGION", "Himoya va harakat yo‘nalishlariga aralashadi."),
    ("solnomachi", "📜 Solnomachi", "LEGION", "O‘yindagi muhim voqealarni kuzatadi."),
    ("savdogar", "💰 Savdogar", "LEGION", "Savdo va resurs mexanikalariga bog‘lanadi."),
    ("suiqasdchi", "🗡️ Suiqasdchi", "LEGION", "Mustaqil yashirin hujum qobiliyatiga ega."),
    ("oshpaz", "🍳 Oshpaz", "LEGION", "Kechasi bir o‘yinchiga ovqat tayyorlaydi."),
]


# =========================
# GURUH NOMLARI
# =========================

TEAM_LABELS = {
    "KRON": "KRON",
    "SOYA": "SOYA",
    "YAKKA": "YAKKA",
    "LEGION": "LEGION",
}


# =========================
# ROLE MAP
# =========================

ROLE_MAP = {
    role_id: {
        "id": role_id,
        "name": name,
        "team": team,
        "side": TEAM_LABELS[team],
        "description": description,
    }
    for role_id, name, team, description in ROLES
}


ROLE_KEYS = tuple(ROLE_MAP.keys())


TEAM_ROLES = {
    team: tuple(
        role_id
        for role_id, role in ROLE_MAP.items()
        if role["team"] == team
    )
    for team in TEAM_LABELS
}


# =========================
# TEKSHIRUVLAR
# =========================

assert len(ROLES) == 36, "THRONE 36 ta rol bo‘lishi kerak."

assert len(ROLE_MAP) == 36, "Role ID lar takrorlangan."

assert (
    len(TEAM_ROLES["KRON"]) == 12
), "KRON 12 ta rol bo‘lishi kerak."

assert (
    len(TEAM_ROLES["SOYA"]) == 10
), "SOYA 10 ta rol bo‘lishi kerak."

assert (
    len(TEAM_ROLES["YAKKA"]) == 7
), "YAKKA 7 ta rol bo‘lishi kerak."

assert (
    len(TEAM_ROLES["LEGION"]) == 7
), "LEGION 7 ta rol bo‘lishi kerak."


def get_role(role_id: str):
    """Rol ma’lumotini qaytaradi."""
    return ROLE_MAP.get(role_id)


def get_roles_by_team(team: str):
    """Berilgan guruhdagi barcha rollarni qaytaradi."""
    return [
        ROLE_MAP[role_id]
        for role_id in TEAM_ROLES.get(team, ())
    ]


def all_roles():
    """Barcha 36 ta rolni qaytaradi."""
    return list(ROLE_MAP.values())
