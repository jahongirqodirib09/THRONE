"""THRONE — 36 ta asosiy rol (README dagi ro'yxat asosida).

Bu fayl rol KALITLARI, nomlari, tomonlari va README dagi tavsifni belgilaydi.
Rol mexanikalari (tungi/kunduzgi qobiliyat, cooldown, foydalanish soni,
g'alaba sharti) alohida tasdiqlanadi va role_engine.py / game_victory.py ga yoziladi.

Tomonlar (team):
  THRONE — Taxt / Qirollik (12)
  SHADOW — Soya / Dushman (10)
  YAKKA  — Yakka (7)
  MAXSUS — Maxsus (7)
"""

# (key, name, team, description)
ROLES = [
    # ---- I. TAXT / QIROLLIK — 12 ----
    ("shoh",              "👑 Shoh",               "THRONE", "Qirollikning markaziy figurasi."),
    ("malika",            "👸 Malika",             "THRONE", "Qirollikdagi yuqori martabali himoya/siyosiy rol."),
    ("shahzoda",          "🤴 Shahzoda",           "THRONE", "Shohning vorisi. Maxsus hokimiyat mexanikalariga ega bo‘lishi mumkin."),
    ("vazir",             "🏛️ Vazir",              "THRONE", "Shohga yaqin siyosiy rol. Muhim qarorlarga ta'sir qilishi mumkin."),
    ("bosh_qomondon",     "⚔️ Bosh qo‘mondon",     "THRONE", "Qirollik harbiy kuchlarining boshlig‘i."),
    ("qirol_qoriqchisi",  "🛡️ Qirol qo‘riqchisi",  "THRONE", "Muhim shaxslarni himoya qiladi."),
    ("qozi",              "⚖️ Qozi",               "THRONE", "Sud va ovoz berish bilan bog‘liq maxsus vakolatlarga ega."),
    ("xazinachi",         "💰 Xazinachi",          "THRONE", "Qirollik xazinasi bilan bog‘liq rol."),
    ("ritsar",            "🏰 Ritsir",             "THRONE", "Jangovar himoya roli."),
    ("xizmatkor",         "🧹 Xizmatkor",          "THRONE", "Oddiy ko‘rinadigan, lekin maxsus yashirin imkoniyatga ega bo‘lishi mumkin."),
    ("tinch_aholi",       "🏘️ Tinch aholi",        "THRONE", "Oddiy qirollik fuqarosi."),
    ("aygoqchi",          "🕵️ Ayg‘oqchi",          "THRONE", "Dushman haqida ma'lumot yig‘ishga ixtisoslashgan."),
    # ---- II. SOYA / DUSHMAN — 10 ----
    ("soya_boshligi",         "🕶️ Soya boshlig‘i",         "SHADOW", "Soya tomonining asosiy rahbari."),
    ("qotil",                 "🗡️ Qotil",                  "SHADOW", "Tungi hujumlarning asosiy ijrochilaridan biri."),
    ("josus",                 "🕵️ Josus",                  "SHADOW", "Qirollik ichiga kirib, ma'lumot yig‘adi."),
    ("soxta_maslahatchi",     "🎭 Soxta maslahatchi",      "SHADOW", "O‘zini qirollik tarafdori qilib ko‘rsatishi mumkin."),
    ("xoin",                  "🩸 Xoin",                   "SHADOW", "Qirollik ichidagi yashirin dushman."),
    ("qora_vazir",            "🖤 Qora vazir",             "SHADOW", "Siyosiy manipulyatsiyaga ixtisoslashgan dushman."),
    ("dushman_qiroli",        "👑 Dushman qiroli",         "SHADOW", "Soya tomonining yuqori hokimiyat figurasi."),
    ("dushman_qomondoni",     "⚔️ Dushman qo‘mondoni",     "SHADOW", "Harbiy yo‘nalishdagi kuchli dushman."),
    ("dushman_josusi",        "🕵️ Dushman josusi",         "SHADOW", "Ma'lumot va kuzatuvga ixtisoslashgan."),
    ("dushman_suiqasdchisi",  "🗡️ Dushman suiqasdchisi",   "SHADOW", "Maxsus yashirin o‘ldirish mexanikasiga ega."),
    # ---- III. YAKKA — 7 ----
    ("ovchi",             "🐺 Ovchi",              "YAKKA", "O‘zining alohida maqsadi bo‘lishi mumkin."),
    ("telba",             "🃏 Telba",              "YAKKA", "Boshqalarga o‘xshamaydigan g‘alaba shartiga ega."),
    ("sayyoh",            "👤 Sayyoh",             "YAKKA", "Qirollik siyosatiga bevosita bog‘lanmagan maxsus rol."),
    ("yollanma_jangchi",  "⚔️ Yollanma jangchi",   "YAKKA", "Kim bilan ittifoq qilishi vaziyatga bog‘liq."),
    ("surgun_shahzoda",   "🤴 Surgun shahzoda",    "YAKKA", "Taxtdan ayrilgan shahzoda. Alohida g‘alaba yo‘li mavjud."),
    ("taxt_davogari",     "👑 Taxt da’vogari",     "YAKKA", "Taxtni egallashga urinuvchi mustaqil kuch."),
    ("qaroqchi",          "🥷 Qaroqchi",           "YAKKA", "Yashirin harakat va resurslar bilan bog‘liq rol."),
    # ---- IV. MAXSUS — 7 ----
    ("sehrgar",           "🧙 Sehrgar",            "MAXSUS", "Maxsus tungi qobiliyatlar."),
    ("tabib",             "🩺 Tabib",              "MAXSUS", "Jarohatlangan yoki hujumga uchragan o‘yinchilarni saqlab qolishi mumkin."),
    ("kuzatuvchi",        "👁️ Kuzatuvchi",         "MAXSUS", "Boshqa o‘yinchilarning harakatlarini kuzatishi mumkin."),
    ("qorovul",           "🔒 Qorovul",            "MAXSUS", "Himoya va qo‘riqlashga ixtisoslashgan."),
    ("solnomachi",        "📜 Solnomachi",         "MAXSUS", "O‘yindagi voqealar va ma'lumotlarni kuzatishga mo‘ljallangan."),
    ("savdogar",          "💰 Savdogar",           "MAXSUS", "Savdo/resurs mexanikalariga bog‘lanadi."),
    ("suiqasdchi",        "🗡️ Suiqasdchi",         "MAXSUS", "Mustaqil yashirin hujum qobiliyatiga ega."),
]

TEAM_LABELS = {
    "THRONE": "Taxt tomoni",
    "SHADOW": "Soya tomoni",
    "YAKKA": "Yakka",
    "MAXSUS": "Maxsus",
}

ROLE_MAP = {
    r[0]: {
        "id": r[0],
        "name": r[1],
        "team": r[2],
        "side": TEAM_LABELS[r[2]],
        "description": r[3],
    }
    for r in ROLES
}

ROLE_KEYS = tuple(ROLE_MAP)
TEAM_ROLES = {t: tuple(k for k, v in ROLE_MAP.items() if v["team"] == t) for t in TEAM_LABELS}

# Import vaqtida tekshiruv: rollar soni va kalitlar noyobligi buzilsa, bot ishga tushmaydi.
assert len(ROLES) == 36, f"36 ta rol kerak, hozir {len(ROLES)}"
assert len(ROLE_MAP) == 36, "Rol kalitlari noyob bo‘lishi kerak"
assert tuple(len(TEAM_ROLES[t]) for t in ("THRONE", "SHADOW", "YAKKA", "MAXSUS")) == (12, 10, 7, 7)
