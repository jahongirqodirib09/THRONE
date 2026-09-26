from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================================
# THRONE — TERRITORY SYSTEM
# ============================================================

MIN_TERRITORY_LEVEL = 1
MAX_TERRITORY_LEVEL = 20

TERRITORY_TYPES = {
    "village": {
        "name": "🏘️ Qishloq",
        "base_income": 100,
        "base_defense": 50,
        "base_value": 500,
    },
    "town": {
        "name": "🏙️ Shahar",
        "base_income": 300,
        "base_defense": 150,
        "base_value": 1500,
    },
    "fortress": {
        "name": "🏰 Qal’a",
        "base_income": 600,
        "base_defense": 400,
        "base_value": 4000,
    },
    "capital": {
        "name": "👑 Poytaxt",
        "base_income": 1200,
        "base_defense": 800,
        "base_value": 10000,
    },
}


@dataclass
class TerritoryResult:
    success: bool
    message: str = ""
    territory_id: Optional[str] = None
    data: Optional[dict] = None


# ============================================================
# BASIC HELPERS
# ============================================================

def get_territory_type(territory_type: str) -> Optional[dict]:
    return TERRITORY_TYPES.get(territory_type)


def get_territory_name(territory_type: str) -> str:
    territory = get_territory_type(territory_type)

    if not territory:
        return "Noma’lum hudud"

    return territory["name"]


def get_all_territory_types() -> Dict[str, dict]:
    return {
        key: dict(value)
        for key, value in TERRITORY_TYPES.items()
    }


def get_territory_level_multiplier(level: int) -> float:
    level = max(
        MIN_TERRITORY_LEVEL,
        min(MAX_TERRITORY_LEVEL, int(level)),
    )

    return 1 + ((level - 1) * 0.15)


def calculate_income(
    territory_type: str,
    level: int = 1,
) -> int:
    territory = get_territory_type(territory_type)

    if not territory:
        return 0

    multiplier = get_territory_level_multiplier(level)

    return int(
        territory["base_income"] * multiplier
    )


def calculate_defense(
    territory_type: str,
    level: int = 1,
) -> int:
    territory = get_territory_type(territory_type)

    if not territory:
        return 0

    multiplier = get_territory_level_multiplier(level)

    return int(
        territory["base_defense"] * multiplier
    )


def calculate_value(
    territory_type: str,
    level: int = 1,
) -> int:
    territory = get_territory_type(territory_type)

    if not territory:
        return 0

    multiplier = get_territory_level_multiplier(level)

    return int(
        territory["base_value"] * multiplier
    )


# ============================================================
# TERRITORY CREATION
# ============================================================

def create_territory(
    territory_id: str,
    name: str,
    territory_type: str = "village",
    owner_id: Optional[int] = None,
    level: int = 1,
) -> TerritoryResult:

    if not territory_id:
        return TerritoryResult(
            success=False,
            message="❌ Hudud ID ko‘rsatilmagan.",
        )

    if not name or not name.strip():
        return TerritoryResult(
            success=False,
            message="❌ Hudud nomi bo‘sh bo‘lishi mumkin emas.",
        )

    if territory_type not in TERRITORY_TYPES:
        return TerritoryResult(
            success=False,
            message="❌ Noto‘g‘ri hudud turi.",
        )

    level = max(
        MIN_TERRITORY_LEVEL,
        min(MAX_TERRITORY_LEVEL, int(level)),
    )

    territory = {
        "id": territory_id,
        "name": name.strip(),
        "type": territory_type,
        "owner_id": owner_id,
        "level": level,
        "income": calculate_income(
            territory_type,
            level,
        ),
        "defense": calculate_defense(
            territory_type,
            level,
        ),
        "value": calculate_value(
            territory_type,
            level,
        ),
        "war_locked": False,
        "under_attack": False,
    }

    return TerritoryResult(
        success=True,
        territory_id=territory_id,
        message=(
            f"🗺️ {name.strip()} hududi yaratildi."
        ),
        data=territory,
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_territory(
    territory: dict,
) -> TerritoryResult:

    if not territory:
        return TerritoryResult(
            success=False,
            message="❌ Hudud ma’lumoti topilmadi.",
        )

    required = [
        "id",
        "name",
        "type",
        "level",
    ]

    for field in required:
        if field not in territory:
            return TerritoryResult(
                success=False,
                message=(
                    f"❌ Hudud ma’lumotida "
                    f"{field} mavjud emas."
                ),
            )

    if territory["type"] not in TERRITORY_TYPES:
        return TerritoryResult(
            success=False,
            message="❌ Hudud turi noto‘g‘ri.",
        )

    return TerritoryResult(
        success=True,
        message="✅ Hudud ma’lumotlari to‘g‘ri.",
        territory_id=str(territory["id"]),
        data=territory,
    )


# ============================================================
# OWNERSHIP
# ============================================================

def is_owner(
    territory: dict,
    user_id: int,
) -> bool:

    return territory.get("owner_id") == user_id


def can_capture(
    territory: dict,
    attacker_id: int,
) -> TerritoryResult:

    if not territory:
        return TerritoryResult(
            success=False,
            message="❌ Hudud topilmadi.",
        )

    if territory.get("owner_id") == attacker_id:
        return TerritoryResult(
            success=False,
            message="❌ O‘z hududingizni bosib olmaysiz.",
        )

    if territory.get("war_locked"):
        return TerritoryResult(
            success=False,
            message="❌ Bu hudud hozircha urush uchun yopilgan.",
        )

    if territory.get("under_attack"):
        return TerritoryResult(
            success=False,
            message="❌ Bu hudud allaqachon hujum ostida.",
        )

    return TerritoryResult(
        success=True,
        message="✅ Hudud uchun urush boshlash mumkin.",
        territory_id=str(territory["id"]),
    )


def transfer_territory(
    territory: dict,
    new_owner_id: int,
) -> TerritoryResult:

    if not territory:
        return TerritoryResult(
            success=False,
            message="❌ Hudud topilmadi.",
        )

    if not new_owner_id:
        return TerritoryResult(
            success=False,
            message="❌ Yangi egasi aniqlanmadi.",
        )

    old_owner = territory.get("owner_id")

    territory["owner_id"] = new_owner_id
    territory["under_attack"] = False
    territory["war_locked"] = False

    return TerritoryResult(
        success=True,
        territory_id=str(territory["id"]),
        message=(
            f"👑 Hudud yangi hukmdorga o‘tdi."
        ),
        data={
            "old_owner_id": old_owner,
            "new_owner_id": new_owner_id,
        },
    )


# ============================================================
# TERRITORY LEVEL
# ============================================================

def get_level_upgrade_cost(
    territory: dict,
) -> int:

    level = int(
        territory.get(
            "level",
            MIN_TERRITORY_LEVEL,
        )
    )

    if level >= MAX_TERRITORY_LEVEL:
        return 0

    base = calculate_value(
        territory.get("type", "village"),
        level,
    )

    return int(base * 0.35)


def can_upgrade_territory(
    territory: dict,
) -> TerritoryResult:

    if not territory:
        return TerritoryResult(
            success=False,
            message="❌ Hudud topilmadi.",
        )

    level = int(
        territory.get("level", 1)
    )

    if level >= MAX_TERRITORY_LEVEL:
        return TerritoryResult(
            success=False,
            message="🏆 Hudud maksimal darajaga yetgan.",
        )

    cost = get_level_upgrade_cost(
        territory
    )

    return TerritoryResult(
        success=True,
        message=(
            f"⬆️ Hududni {level + 1}-darajaga "
            f"ko‘tarish mumkin.\n"
            f"🟡 Narx: {cost} oltin"
        ),
        data={
            "current_level": level,
            "next_level": level + 1,
            "cost": cost,
        },
    )


def upgrade_territory(
    territory: dict,
) -> TerritoryResult:

    check = can_upgrade_territory(
        territory
    )

    if not check.success:
        return check

    old_level = int(
        territory.get("level", 1)
    )

    new_level = old_level + 1

    territory["level"] = new_level

    territory["income"] = calculate_income(
        territory["type"],
        new_level,
    )

    territory["defense"] = calculate_defense(
        territory["type"],
        new_level,
    )

    territory["value"] = calculate_value(
        territory["type"],
        new_level,
    )

    return TerritoryResult(
        success=True,
        territory_id=str(
            territory["id"]
        ),
        message=(
            f"⬆️ {territory['name']} "
            f"{new_level}-darajaga ko‘tarildi."
        ),
        data={
            "old_level": old_level,
            "new_level": new_level,
            "income": territory["income"],
            "defense": territory["defense"],
            "value": territory["value"],
        },
    )


# ============================================================
# WAR
# ============================================================

def start_territory_attack(
    territory: dict,
    attacker_id: int,
) -> TerritoryResult:

    check = can_capture(
        territory,
        attacker_id,
    )

    if not check.success:
        return check

    territory["under_attack"] = True
    territory["war_locked"] = True

    return TerritoryResult(
        success=True,
        territory_id=str(
            territory["id"]
        ),
        message=(
            f"⚔️ {territory['name']} "
            "hududiga hujum boshlandi."
        ),
        data={
            "attacker_id": attacker_id,
            "defender_id": territory.get(
                "owner_id"
            ),
        },
    )


def resolve_territory_war(
    territory: dict,
    attacker_id: int,
    attacker_power: int,
    defender_power: int,
) -> TerritoryResult:

    if not territory:
        return TerritoryResult(
            success=False,
            message="❌ Hudud topilmadi.",
        )

    if not territory.get("under_attack"):
        return TerritoryResult(
            success=False,
            message="❌ Bu hududda faol urush yo‘q.",
        )

    attacker_power = max(
        0,
        int(attacker_power),
    )

    defender_power = max(
        0,
        int(defender_power),
    )

    old_owner = territory.get(
        "owner_id"
    )

    territory["under_attack"] = False
    territory["war_locked"] = False

    if attacker_power > defender_power:

        territory["owner_id"] = attacker_id

        return TerritoryResult(
            success=True,
            territory_id=str(
                territory["id"]
            ),
            message=(
                f"🏰 {territory['name']} "
                "yangi qirollik nazoratiga o‘tdi."
            ),
            data={
                "winner": "attacker",
                "attacker_id": attacker_id,
                "old_owner_id": old_owner,
                "new_owner_id": attacker_id,
                "attacker_power": attacker_power,
                "defender_power": defender_power,
            },
        )

    if defender_power > attacker_power:

        return TerritoryResult(
            success=True,
            territory_id=str(
                territory["id"]
            ),
            message=(
                f"🛡️ {territory['name']} "
                "himoya qilindi."
            ),
            data={
                "winner": "defender",
                "attacker_id": attacker_id,
                "owner_id": old_owner,
                "attacker_power": attacker_power,
                "defender_power": defender_power,
            },
        )

    return TerritoryResult(
        success=True,
        territory_id=str(
            territory["id"]
        ),
        message=(
            f"⚖️ {territory['name']} uchun "
            "jang durang bilan yakunlandi."
        ),
        data={
            "winner": "draw",
            "attacker_id": attacker_id,
            "owner_id": old_owner,
            "attacker_power": attacker_power,
            "defender_power": defender_power,
        },
    )


# ============================================================
# ECONOMY
# ============================================================

def collect_income(
    territory: dict,
) -> TerritoryResult:

    if not territory:
        return TerritoryResult(
            success=False,
            message="❌ Hudud topilmadi.",
        )

    owner_id = territory.get(
        "owner_id"
    )

    if not owner_id:
        return TerritoryResult(
            success=False,
            message="❌ Hududning egasi yo‘q.",
        )

    income = calculate_income(
        territory.get("type", "village"),
        territory.get("level", 1),
    )

    return TerritoryResult(
        success=True,
        territory_id=str(
            territory["id"]
        ),
        message=(
            f"🟡 {territory['name']} "
            f"hududidan {income} oltin daromad olindi."
        ),
        data={
            "owner_id": owner_id,
            "income": income,
        },
    )


def get_territory_economy(
    territory: dict,
) -> dict:

    if not territory:
        return {
            "income": 0,
            "value": 0,
            "defense": 0,
        }

    return {
        "income": calculate_income(
            territory.get("type", "village"),
            territory.get("level", 1),
        ),
        "value": calculate_value(
            territory.get("type", "village"),
            territory.get("level", 1),
        ),
        "defense": calculate_defense(
            territory.get("type", "village"),
            territory.get("level", 1),
        ),
    }


# ============================================================
# DEFENSE
# ============================================================

def reinforce_territory(
    territory: dict,
    bonus_defense: int,
) -> TerritoryResult:

    if not territory:
        return TerritoryResult(
            success=False,
            message="❌ Hudud topilmadi.",
        )

    bonus_defense = max(
        0,
        int(bonus_defense),
    )

    territory["defense"] = int(
        territory.get("defense", 0)
    ) + bonus_defense

    return TerritoryResult(
        success=True,
        territory_id=str(
            territory["id"]
        ),
        message=(
            f"🛡️ {territory['name']} "
            f"mudofaasi +{bonus_defense} ga oshirildi."
        ),
        data={
            "defense": territory["defense"],
        },
    )


def get_defense_status(
    territory: dict,
) -> str:

    defense = int(
        territory.get("defense", 0)
    )

    if defense >= 1000:
        return "🟢 Juda kuchli"

    if defense >= 600:
        return "🟢 Kuchli"

    if defense >= 300:
        return "🟡 O‘rtacha"

    if defense >= 100:
        return "🟠 Zaif"

    return "🔴 Juda zaif"


# ============================================================
# TERRITORY TEXT
# ============================================================

def territory_text(
    territory: dict,
) -> str:

    if not territory:
        return "❌ Hudud topilmadi."

    territory_type = territory.get(
        "type",
        "village",
    )

    level = int(
        territory.get("level", 1)
    )

    income = calculate_income(
        territory_type,
        level,
    )

    defense = int(
        territory.get(
            "defense",
            calculate_defense(
                territory_type,
                level,
            ),
        )
    )

    value = calculate_value(
        territory_type,
        level,
    )

    owner = territory.get(
        "owner_id"
    )

    owner_text = (
        str(owner)
        if owner
        else "Erkin hudud"
    )

    return (
        f"🗺️ {territory.get('name', 'Noma’lum')}\n"
        f"🏷️ Turi: {get_territory_name(territory_type)}\n"
        f"📈 Daraja: {level}/{MAX_TERRITORY_LEVEL}\n"
        f"👑 Egasi: {owner_text}\n\n"
        f"🟡 Daromad: {income}/davr\n"
        f"🛡️ Mudofaa: {defense}\n"
        f"📊 Qiymat: {value}\n"
        f"🔰 Holat: {get_defense_status(territory)}"
    )


def territory_dashboard(
    territories: List[dict],
    owner_id: Optional[int] = None,
) -> str:

    if owner_id is not None:
        territories = [
            territory
            for territory in territories
            if territory.get("owner_id")
            == owner_id
        ]

    if not territories:
        return (
            "🗺️ HUDUDLAR\n\n"
            "Hozircha hudud mavjud emas."
        )

    total_income = sum(
        calculate_income(
            territory.get("type", "village"),
            territory.get("level", 1),
        )
        for territory in territories
    )

    total_defense = sum(
        int(
            territory.get(
                "defense",
                0,
            )
        )
        for territory in territories
    )

    total_value = sum(
        calculate_value(
            territory.get("type", "village"),
            territory.get("level", 1),
        )
        for territory in territories
    )

    lines = [
        "🗺️ QIROLLIK HUDUDLARI",
        "",
        f"🏰 Hududlar: {len(territories)}",
        f"🟡 Umumiy daromad: {total_income}",
        f"🛡️ Umumiy mudofaa: {total_defense}",
        f"💰 Umumiy qiymat: {total_value}",
        "",
    ]

    for territory in territories:
        lines.append(
            f"• {territory.get('name', 'Noma’lum')} "
            f"— {territory.get('level', 1)}-daraja"
        )

    return "\n".join(lines)


# ============================================================
# RANKING
# ============================================================

def calculate_kingdom_territory_power(
    territories: List[dict],
    owner_id: int,
) -> int:

    owned = [
        territory
        for territory in territories
        if territory.get("owner_id")
        == owner_id
    ]

    power = 0

    for territory in owned:

        level = int(
            territory.get("level", 1)
        )

        defense = int(
            territory.get("defense", 0)
        )

        income = calculate_income(
            territory.get("type", "village"),
            level,
        )

        power += (
            level * 100
            + defense
            + income
        )

    return power


def territory_ranking(
    territories: List[dict],
) -> List[dict]:

    owners = {}

    for territory in territories:

        owner_id = territory.get(
            "owner_id"
        )

        if not owner_id:
            continue

        owners.setdefault(
            owner_id,
            [],
        ).append(
            territory
        )

    ranking = []

    for owner_id, owner_territories in owners.items():

        power = calculate_kingdom_territory_power(
            territories,
            owner_id,
        )

        ranking.append(
            {
                "owner_id": owner_id,
                "territories": len(
                    owner_territories
                ),
                "power": power,
            }
        )

    ranking.sort(
        key=lambda item: item["power"],
        reverse=True,
    )

    for inde
