# ============================================================
# THRONE — KINGDOM SYSTEM
# ============================================================

from dataclasses import dataclass
from typing import Optional

from config import CREATOR_ID
from database import (
    get_user,
    create_kingdom,
    get_kingdom,
    get_castle,
    get_army,
)


# ============================================================
# CONSTANTS
# ============================================================

MAX_KINGDOM_LEVEL = 100
MAX_CASTLE_LEVEL = 100

BASE_DEFENSE = 100
BASE_POPULATION = 10

KINGDOM_LEVEL_GOLD_COST = 1_000
CASTLE_LEVEL_GOLD_COST = 1_500

SOLDIER_COST = 50
ARCHER_COST = 75
GUARD_COST = 100
CAVALRY_COST = 150


# ============================================================
# RESULT
# ============================================================

@dataclass
class KingdomResult:
    success: bool
    message: str
    data: Optional[dict] = None


# ============================================================
# CREATOR
# ============================================================

def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


# ============================================================
# DEFAULT KINGDOM
# ============================================================

def default_kingdom_data(user_id: int) -> dict:

    return {
        "owner_id": user_id,
        "name": "THRONE Qirolligi",
        "flag": "👑",
        "level": 1,
        "gold": 0,
        "population": BASE_POPULATION,
        "defense": BASE_DEFENSE,
        "military_power": 0,
    }


# ============================================================
# GET KINGDOM
# ============================================================

async def load_kingdom(
    user_id: int,
) -> Optional[dict]:

    kingdom = await get_kingdom(user_id)

    if kingdom:
        return kingdom

    return None


# ============================================================
# CREATE KINGDOM
# ============================================================

async def create_player_kingdom(
    user_id: int,
    name: str = "THRONE Qirolligi",
    flag: str = "👑",
) -> KingdomResult:

    user = await get_user(user_id)

    if not user:
        return KingdomResult(
            False,
            "❌ O‘yinchi topilmadi.",
        )

    existing = await get_kingdom(user_id)

    if existing:
        return KingdomResult(
            False,
            "❌ Sizda allaqachon qirollik mavjud.",
            existing,
        )

    if not name.strip():
        return KingdomResult(
            False,
            "❌ Qirollik nomi bo‘sh bo‘lishi mumkin emas.",
        )

    if len(name.strip()) > 40:
        return KingdomResult(
            False,
            "❌ Qirollik nomi 40 belgidan oshmasin.",
        )

    try:
        result = await create_kingdom(
            user_id,
            name.strip(),
            flag,
        )

        return KingdomResult(
            True,
            (
                "👑 QIROLLIK YARATILDI!\n\n"
                f"{flag} {name.strip()}\n\n"
                "🏰 Qal’a: 1-daraja\n"
                "🛡️ Mudofaa: 100\n"
                "👥 Aholi: 10\n"
                "⚔️ Harbiy kuch: 0"
            ),
            result,
        )

    except Exception as exc:
        return KingdomResult(
            False,
            f"❌ Qirollik yaratishda xatolik: {exc}",
        )


# ============================================================
# KINGDOM NAME
# ============================================================

async def rename_kingdom(
    user_id: int,
    new_name: str,
) -> KingdomResult:

    kingdom = await get_kingdom(user_id)

    if not kingdom:
        return KingdomResult(
            False,
            "❌ Avval qirollik yarating.",
        )

    new_name = new_name.strip()

    if not new_name:
        return KingdomResult(
            False,
            "❌ Nom bo‘sh bo‘lishi mumkin emas.",
        )

    if len(new_name) > 40:
        return KingdomResult(
            False,
            "❌ Nom 40 belgidan oshmasin.",
        )

    # Database'da umumiy update helper bo‘lmagani uchun
    # bu funksiya yuqori modul orqali ulanish uchun tayyorlangan.
    return KingdomResult(
        True,
        f"👑 Yangi qirollik nomi: {new_name}",
        {
            "name": new_name,
        },
    )


# ============================================================
# KINGDOM SUMMARY
# ============================================================

async def kingdom_summary(
    user_id: int,
) -> KingdomResult:

    kingdom = await get_kingdom(user_id)

    if not kingdom:
        return KingdomResult(
            False,
            (
                "🏰 Sizda hali qirollik yo‘q.\n\n"
                "Avval o‘z qirolligingizni yarating."
            ),
        )

    name = kingdom.get(
        "name",
        "THRONE Qirolligi",
    )

    flag = kingdom.get(
        "flag",
        "👑",
    )

    level = kingdom.get(
        "level",
        1,
    )

    gold = kingdom.get(
        "gold",
        0,
    )

    population = kingdom.get(
        "population",
        BASE_POPULATION,
    )

    defense = kingdom.get(
        "defense",
        BASE_DEFENSE,
    )

    military_power = kingdom.get(
        "military_power",
        0,
    )

    return KingdomResult(
        True,
        (
            "🏰 QIROLLIK\n\n"
            f"{flag} {name}\n\n"
            f"⭐ Daraja: {level}\n"
            f"💰 Xazina: {gold:,}\n"
            f"👥 Aholi: {population:,}\n"
            f"🛡️ Mudofaa: {defense:,}\n"
            f"⚔️ Harbiy kuch: {military_power:,}"
        ),
        kingdom,
    )


# ============================================================
# CASTLE SUMMARY
# ============================================================

async def castle_summary(
    user_id: int,
) -> KingdomResult:

    castle = await get_castle(user_id)

    if not castle:
        return KingdomResult(
            False,
            (
                "🏰 QAL’A\n\n"
                "Qal’a ma’lumotlari hali mavjud emas."
            ),
        )

    level = castle.get(
        "level",
        1,
    )

    defense = castle.get(
        "defense",
        0,
    )

    guards = castle.get(
        "guards",
        0,
    )

    treasury_capacity = castle.get(
        "treasury_capacity",
        0,
    )

    return KingdomResult(
        True,
        (
            "🏰 QAL’A\n\n"
            f"⭐ Daraja: {level}\n"
            f"🛡️ Himoya: {defense:,}\n"
            f"👥 Qo‘riqchilar: {guards:,}\n"
            f"💰 Xazina sig‘imi: {treasury_capacity:,}"
        ),
        castle,
    )


# ============================================================
# ARMY SUMMARY
# ============================================================

async def army_summary(
    user_id: int,
) -> KingdomResult:

    army = await get_army(user_id)

    if not army:
        return KingdomResult(
            False,
            "⚔️ Armiya ma’lumotlari hali mavjud emas.",
        )

    soldiers = army.get(
        "soldiers",
        0,
    )

    archers = army.get(
        "archers",
        0,
    )

    guards = army.get(
        "guards",
        0,
    )

    cavalry = army.get(
        "cavalry",
        0,
    )

    total = (
        soldiers
        + archers
        + guards
        + cavalry
    )

    power = calculate_military_power(
        soldiers,
        archers,
        guards,
        cavalry,
    )

    return KingdomResult(
        True,
        (
            "⚔️ ARMIYA\n\n"
            f"⚔️ Askarlar: {soldiers:,}\n"
            f"🏹 Kamonchilar: {archers:,}\n"
            f"🛡️ Qo‘riqchilar: {guards:,}\n"
            f"🐎 Suvariylar: {cavalry:,}\n\n"
            f"👥 Jami: {total:,}\n"
            f"💥 Harbiy kuch: {power:,}"
        ),
        {
            "soldiers": soldiers,
            "archers": archers,
            "guards": guards,
            "cavalry": cavalry,
            "total": total,
            "power": power,
        },
    )


# ============================================================
# MILITARY POWER
# ============================================================

def calculate_military_power(
    soldiers: int,
    archers: int,
    guards: int,
    cavalry: int,
) -> int:

    return (
        soldiers * 1
        + archers * 2
        + guards * 3
        + cavalry * 4
    )


# ============================================================
# CASTLE DEFENSE
# ============================================================

def calculate_castle_defense(
    level: int,
    guards: int,
) -> int:

    level = max(
        1,
        level,
    )

    guards = max(
        0,
        guards,
    )

    return (
        BASE_DEFENSE
        + (level - 1) * 50
        + guards * 5
    )


# ============================================================
# KINGDOM POWER
# ============================================================

def calculate_kingdom_power(
    defense: int,
    military_power: int,
    population: int,
) -> int:

    return (
        defense
        + military_power
        + population
    )


# ============================================================
# LEVEL REQUIREMENT
# ============================================================

def kingdom_level_cost(
    level: int,
) -> int:

    return (
        max(1, level)
        * KINGDOM_LEVEL_GOLD_COST
    )


# ============================================================
# CASTLE LEVEL COST
# ============================================================

def castle_level_cost(
    level: int,
) -> int:

    return (
        max(1, level)
        * CASTLE_LEVEL_GOLD_COST
    )


# ============================================================
# CAN UPGRADE KINGDOM
# ============================================================

def can_upgrade_kingdom(
    current_level: int,
) -> KingdomResult:

    if current_level >= MAX_KINGDOM_LEVEL:
        return KingdomResult(
            False,
            "🏰 Qirollik maksimal darajaga yetgan.",
        )

    cost = kingdom_level_cost(
        current_level,
    )

    return KingdomResult(
        True,
        (
            "⬆️ QIROLLIKNI RIVOJLANTIRISH\n\n"
            f"Joriy daraja: {current_level}\n"
            f"Keyingi daraja: {current_level + 1}\n"
            f"🟡 Narx: {cost:,}"
        ),
        {
            "next_level": current_level + 1,
            "cost": cost,
        },
    )


# ============================================================
# CAN UPGRADE CASTLE
# ============================================================

def can_upgrade_castle(
    current_level: int,
) -> KingdomResult:

    if current_level >= MAX_CASTLE_LEVEL:
        return KingdomResult(
            False,
            "🏰 Qal’a maksimal darajaga yetgan.",
        )

    cost = castle_level_cost(
        current_level,
    )

    return KingdomResult(
        True,
        (
            "🏰 QAL’ANI RIVOJLANTIRISH\n\n"
            f"Joriy daraja: {current_level}\n"
            f"Keyingi daraja: {current_level + 1}\n"
            f"🟡 Narx: {cost:,}"
        ),
        {
            "next_level": current_level + 1,
            "cost": cost,
        },
    )


# ============================================================
# ARMY UNIT COST
# ============================================================

def unit_cost(
    unit_type: str,
) -> int:

    costs = {
        "soldier": SOLDIER_COST,
        "archer": ARCHER_COST,
        "guard": GUARD_COST,
        "cavalry": CAVALRY_COST,
    }

    return costs.get(
        unit_type,
        0,
    )


# ============================================================
# ARMY UNIT POWER
# ============================================================

def unit_power(
    unit_type: str,
) -> int:

    powers = {
        "soldier": 1,
        "archer": 2,
        "guard": 3,
        "cavalry": 4,
    }

    return powers.get(
        unit_type,
        0,
    )


# ============================================================
# RECRUITMENT INFORMATION
# ============================================================

def recruitment_info() -> dict:

    return {
        "soldier": {
            "name": "⚔️ Askar",
            "cost": SOLDIER_COST,
            "power": 1,
            "description": "Oddiy jangovar birlik.",
        },
        "archer": {
            "name": "🏹 Kamonchi",
            "cost": ARCHER_COST,
            "power": 2,
            "description": "Masofadan hujum qiluvchi birlik.",
        },
        "guard": {
            "name": "🛡️ Qo‘riqchi",
            "cost": GUARD_COST,
            "power": 3,
            "description": "Qal’a mudofaasini kuchaytiradi.",
        },
        "cavalry": {
            "name": "🐎 Suvariy",
            "cost": CAVALRY_COST,
            "power": 4,
            "description": "Tezkor va kuchli jangovar birlik.",
        },
    }


# ============================================================
# KINGDOM INFORMATION
# ============================================================

def kingdom_features() -> list:

    return [
        "🏰 Qal’a",
        "👑 Taxt",
        "⚔️ Armiya",
        "🛡️ Mudofaa",
        "💰 Qirollik xazinasi",
        "🗺️ Hududlar",
        "🏴 Klanlar",
        "⚔️ Urushlar",
        "📊 Qirollik reytingi",
    ]


# ============================================================
# TERRITORY VALUE
# ============================================================

def territory_value(
    level: int,
    strategic_bonus: int = 0,
) -> int:

    level = max(
        1,
        level,
    )

    strategic_bonus = max(
        0,
        strategic_bonus,
    )

    return (
        level * 100
        + strategic_bonus
    )


# ============================================================
# TERRITORY INCOME
# ============================================================

def territory_income(
    level: int,
    population: int,
) -> int:

    level = max(
        1,
        level,
    )

    population = max(
        0,
        population,
    )

    return (
        level * 100
        + population * 5
    )


# ============================================================
# WAR POWER
# ============================================================

def calculate_war_power(
    army_power: int,
    castle_defense: int,
    kingdom_level: int,
) -> int:

    return (
        army_power
        + castle_defense
        + kingdom_level * 25
    )


# ============================================================
# CREATOR KINGDOM
# ============================================================

def creator_kingdom_bonus(
    user_id: int,
) -> dict:

    if not is_creator(user_id):
        return {
            "unlimited": False,
        }

    return {
        "unlimited": True,
        "gold": float("inf"),
        "defense": float("inf"),
        "military_power": float("inf"),
        "territory": True,
    }


# ============================================================
# KINGDOM DASHBOARD
# ============================================================

async def kingdom_dashboard(
    user_id: int,
) -> dict:

    kingdom = await get_kingdom(
        user_id
    )

    castle = await get_castle(
        user_id
    )

    army = await get_army(
        user_id
    )

    if not kingdom:
        return {
            "exists": False,
            "user_id": user_id,
        }

    kingdom_level = kingdom.get(
        "level",
        1,
    )

    defense = kingdom.get(
        "defense",
        BASE_DEFENSE,
    )

    population = kingdom.get(
        "population",
        BASE_POPULATION,
    )

    if castle:
        castle_level = castle.get(
            "level",
            1,
        )
        castle_defense = castle.get(
            "defense",
            0,
        )
    else:
        castle_level = 1
        castle_defense = 0

    if army:
        military_power = calculate_military_power(
            army.get("soldiers", 0),
            army.get("archers", 0),
            army.get("guards", 0),
            army.get("cavalry", 0),
        )
    else:
        military_power = 0

    total_power = calculate_kingdom_power(
        defense,
        military_power,
        population,
    )

    war_power = calculate_war_power(
        military_power,
        castle_defense,
        kingdom_level,
    )

    return {
        "exists": True,
        "user_id": user_id,
        "name": kingdom.get(
            "name",
            "THRONE Qirolligi",
        ),
        "flag": kingdom.get(
            "flag",
            "👑",
        ),
        "level": kingdom_level,
        "gold": kingdom.get(
            "gold",
            0,
        ),
        "population": population,
        "defense": defense,
        "military_power": military_power,
        "castle_level": castle_level,
        "castle_defense": castle_defense,
        "total_power": total_power,
        "war_power": war_power,
        "creator": is_creator(user_id),
    }


# ============================================================
# KINGDOM STATUS TEXT
# ============================================================

async def kingdom_status_text(
    user_id: int,
) -> str:

    data = await kingdom_dashboard(
        user_id
    )

    if not data.get("exists"):
        return (
            "🏰 QIROLLIK\n\n"
            "Sizda hali qirollik mavjud emas."
        )

    gold = data["gold"]

    if is_creator(user_id):
        gold_text = "∞"
    else:
        gold_text = f"{gold:,}"

    return (
        "👑 THRONE QIROLLIGI\n\n"
        f"{data['flag']} {data['name']}\n\n"
        f"⭐ Qirollik darajasi: {data['level']}\n"
        f"🏰 Qal’a darajasi: {data['castle_level']}\n"
        f"💰 Xazina: {gold_text}\n"
        f"👥 Aholi: {data['population']:,}\n"
        f"🛡️ Mudofaa: {data['defense']:,}\n"
        f"⚔️ Harbiy kuch: {data['military_power']:,}\n"
        f"💥 Umumiy kuch: {data['total_power']:,}\n"
        f"⚔️ Urush kuchi: {data['war_power']:,}"
    )


# ============================================================
# VALIDATE KINGDOM NAME
# ============================================================

def validate_kingdom_name(
    name: str,
) -> KingdomResult:

    name = name.strip()

    if len(name) < 3:
        return KingdomResult(
            False,
            "❌ Qirollik nomi kamida 3 belgidan iborat bo‘lsin.",
        )

    if len(name) > 40:
        return KingdomResult(
            False,
            "❌ Qirollik nomi 40 belgidan oshmasin.",
        )

    return KingdomResult(
        True,
        "✅ Qirollik nomi qabul qilindi.",
        {
            "name": name,
        },
    )


# ============================================================
# VALIDATE FLAG
# ============================================================

def validate_flag(
    flag: str,
) -> KingdomResult:

    flag = flag.strip()

    if not flag:
        return KingdomResult(
            False,
            "❌ Bayroq tanlanmagan.",
        )

    if len(flag) > 8:
        return KingdomResult(
            False,
            "❌ Bayroq juda uzun.",
        )

    return KingdomResult(
        True,
        "✅ Bayroq qabul qilindi.",
        {
            "flag": flag,
        },
        )
