# ============================================================
# THRONE — FAMILY SYSTEM
# ============================================================

from dataclasses import dataclass
from typing import Optional

from config import CREATOR_ID
from database import get_user


# ============================================================
# CONSTANTS
# ============================================================

FAMILY_LEVEL_MIN = 1
FAMILY_LEVEL_MAX = 100

FAMILY_BASE_LEVEL = 1
FAMILY_BASE_GOLD = 0
FAMILY_BASE_POWER = 0

PROPOSAL_PENDING = "pending"
PROPOSAL_ACCEPTED = "accepted"
PROPOSAL_REJECTED = "rejected"
PROPOSAL_CANCELLED = "cancelled"

MARRIAGE_ACTIVE = "active"
MARRIAGE_ENDED = "ended"

FAMILY_BONUS_GOLD = 100
FAMILY_BONUS_POWER = 5


# ============================================================
# RESULT
# ============================================================

@dataclass
class FamilyResult:
    success: bool
    message: str
    data: Optional[dict] = None


# ============================================================
# CREATOR
# ============================================================

def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


# ============================================================
# DEFAULT FAMILY
# ============================================================

def create_family_data(
    user1_id: int,
    user2_id: int,
    married_at: Optional[str] = None,
) -> dict:

    return {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "level": FAMILY_BASE_LEVEL,
        "gold": FAMILY_BASE_GOLD,
        "power": FAMILY_BASE_POWER,
        "status": MARRIAGE_ACTIVE,
        "married_at": married_at,
    }


# ============================================================
# VALIDATE USERS
# ============================================================

async def validate_marriage_users(
    proposer_id: int,
    target_id: int,
) -> FamilyResult:

    if proposer_id == target_id:
        return FamilyResult(
            False,
            "❌ O‘zingizga nikoh taklifi yubora olmaysiz.",
        )

    proposer = await get_user(proposer_id)
    target = await get_user(target_id)

    if not proposer:
        return FamilyResult(
            False,
            "❌ Taklif yuboruvchi o‘yinchi topilmadi.",
        )

    if not target:
        return FamilyResult(
            False,
            "❌ Taklif yuboriladigan o‘yinchi topilmadi.",
        )

    return FamilyResult(
        True,
        "✅ O‘yinchilar tekshirildi.",
        {
            "proposer": proposer,
            "target": target,
        },
    )


# ============================================================
# PROPOSAL
# ============================================================

async def create_marriage_proposal(
    proposer_id: int,
    target_id: int,
) -> FamilyResult:

    validation = await validate_marriage_users(
        proposer_id,
        target_id,
    )

    if not validation.success:
        return validation

    return FamilyResult(
        True,
        (
            "💍 NIKOH TAKLIFI\n\n"
            f"👤 Taklif yuboruvchi: {proposer_id}\n"
            f"❤️ Taklif qabul qiluvchi: {target_id}\n\n"
            "Ushbu taklifga javob bering."
        ),
        {
            "proposer_id": proposer_id,
            "target_id": target_id,
            "status": PROPOSAL_PENDING,
        },
    )


# ============================================================
# ACCEPT PROPOSAL
# ============================================================

def accept_marriage_proposal(
    proposer_id: int,
    target_id: int,
) -> FamilyResult:

    family = create_family_data(
        proposer_id,
        target_id,
    )

    return FamilyResult(
        True,
        (
            "💍 THRONE — NIKOH TASDIQLANDI\n\n"
            f"❤️ {proposer_id} va {target_id}\n"
            "bugundan boshlab bir oilaning vakiliga aylandi.\n\n"
            "🏰 Ikki qalb — bitta xonadon.\n"
            "🤝 Birga qurilgan yo‘l, birga himoya qilinadigan oila.\n\n"
            "✨ Nikohingiz muborak bo‘lsin!\n\n"
            "👑 THRONE’da ba’zi rishtalar tojdan ham qadrli."
        ),
        family,
    )


# ============================================================
# REJECT PROPOSAL
# ============================================================

def reject_marriage_proposal(
    proposer_id: int,
    target_id: int,
) -> FamilyResult:

    return FamilyResult(
        True,
        (
            "💍 NIKOH TAKLIFI\n\n"
            f"👤 {target_id} nikoh taklifini qabul qilmadi."
        ),
        {
            "proposer_id": proposer_id,
            "target_id": target_id,
            "status": PROPOSAL_REJECTED,
        },
    )


# ============================================================
# CANCEL PROPOSAL
# ============================================================

def cancel_marriage_proposal(
    proposer_id: int,
    target_id: int,
) -> FamilyResult:

    return FamilyResult(
        True,
        (
            "❌ NIKOH TAKLIFI BEKOR QILINDI\n\n"
            f"👤 Taklif: {proposer_id} → {target_id}"
        ),
        {
            "proposer_id": proposer_id,
            "target_id": target_id,
            "status": PROPOSAL_CANCELLED,
        },
    )


# ============================================================
# FAMILY MEMBERS
# ============================================================

def get_family_partner(
    family: dict,
    user_id: int,
) -> Optional[int]:

    user1 = family.get(
        "user1_id"
    )

    user2 = family.get(
        "user2_id"
    )

    if user_id == user1:
        return user2

    if user_id == user2:
        return user1

    return None


def is_family_member(
    family: dict,
    user_id: int,
) -> bool:

    return get_family_partner(
        family,
        user_id,
    ) is not None


# ============================================================
# FAMILY LEVEL
# ============================================================

def family_level_cost(
    current_level: int,
) -> int:

    current_level = max(
        FAMILY_LEVEL_MIN,
        current_level,
    )

    return current_level * 1_000


def family_member_limit(
    level: int,
) -> int:

    # Hozir nikoh ikki kishilik.
    # Kelajakdagi oilaviy tizimlar uchun alohida limit.
    return 2


# ============================================================
# FAMILY POWER
# ============================================================

def calculate_family_power(
    level: int,
    gold: int,
) -> int:

    level = max(
        FAMILY_LEVEL_MIN,
        level,
    )

    gold = max(
        0,
        gold,
    )

    return (
        level * 50
        + gold // 1_000
    )


# ============================================================
# FAMILY BONUS
# ============================================================

def calculate_family_bonus(
    level: int,
) -> dict:

    level = max(
        FAMILY_LEVEL_MIN,
        level,
    )

    return {
        "gold": FAMILY_BONUS_GOLD * level,
        "power": FAMILY_BONUS_POWER * level,
        "level": level,
    }


# ============================================================
# FAMILY BENEFITS
# ============================================================

def family_benefits(
    level: int,
) -> list:

    level = max(
        FAMILY_LEVEL_MIN,
        level,
    )

    return [
        "❤️ Oilaviy status",
        "💰 Umumiy oilaviy bonus",
        "⭐ Oila darajasi",
        "⚔️ Oilaviy kuch",
        "🎁 Maxsus oilaviy mukofotlar",
        f"👑 Oila darajasi: {level}",
    ]


# ============================================================
# FAMILY LEVEL PREVIEW
# ============================================================

def family_level_preview(
    current_level: int,
) -> FamilyResult:

    if current_level >= FAMILY_LEVEL_MAX:
        return FamilyResult(
            False,
            "🏆 Oila maksimal darajaga yetgan.",
        )

    cost = family_level_cost(
        current_level
    )

    return FamilyResult(
        True,
        (
            "⬆️ OILA DARAJASI\n\n"
            f"⭐ Joriy daraja: {current_level}\n"
            f"⬆️ Keyingi daraja: {current_level + 1}\n"
            f"🟡 Narx: {cost:,} oltin"
        ),
        {
            "current_level": current_level,
            "next_level": current_level + 1,
            "cost": cost,
        },
    )


# ============================================================
# FAMILY STATUS
# ============================================================

def family_status_text(
    family: dict,
) -> str:

    status = family.get(
        "status",
        MARRIAGE_ACTIVE,
    )

    statuses = {
        MARRIAGE_ACTIVE: "❤️ Nikoh faol",
        MARRIAGE_ENDED: "💔 Nikoh yakunlangan",
    }

    return statuses.get(
        status,
        "❔ Noma’lum",
    )


# ============================================================
# FAMILY DASHBOARD
# ============================================================

def family_dashboard(
    family: Optional[dict],
    user_id: int,
) -> FamilyResult:

    if not family:
        return FamilyResult(
            True,
            (
                "❤️ OILA\n\n"
                "Siz hozircha nikohda emassiz.\n\n"
                "💍 Nikoh taklifi guruh orqali yuboriladi."
            ),
            {
                "married": False,
            },
        )

    partner_id = get_family_partner(
        family,
        user_id,
    )

    if partner_id is None:
        return FamilyResult(
            False,
            "❌ Oila ma’lumotlari mos kelmadi.",
        )

    level = family.get(
        "level",
        FAMILY_BASE_LEVEL,
    )

    gold = family.get(
        "gold",
        FAMILY_BASE_GOLD,
    )

    power = family.get(
        "power",
        FAMILY_BASE_POWER,
    )

    bonus = calculate_family_bonus(
        level
    )

    return FamilyResult(
        True,
        (
            "❤️ THRONE — OILA\n\n"
            f"💍 Turmush o‘rtog‘i: {partner_id}\n"
            f"⭐ Oila darajasi: {level}\n"
            f"💰 Oilaviy oltin: {gold:,}\n"
            f"⚔️ Oilaviy kuch: {power:,}\n"
            f"❤️ Holat: {family_status_text(family)}\n\n"
            "🎁 Oilaviy bonus:\n"
            f"🟡 +{bonus['gold']:,} oltin\n"
            f"⚔️ +{bonus['power']} kuch"
        ),
        {
            "married": True,
            "partner_id": partner_id,
            "level": level,
            "gold": gold,
            "power": power,
            "bonus": bonus,
        },
    )


# ============================================================
# FAMILY REWARD
# ============================================================

def family_reward(
    family_level: int,
    days_married: int = 0,
) -> dict:

    family_level = max(
        1,
        family_level,
    )

    days_married = max(
        0,
        days_married,
    )

    return {
        "gold": 250 * family_level,
        "coin": max(1, family_level // 5),
        "diamond": max(1, family_level // 20),
        "loyalty": days_married,
    }


# ============================================================
# ANNIVERSARY
# ============================================================

def anniversary_reward(
    family_level: int,
    years: int,
) -> FamilyResult:

    years = max(
        1,
        years,
    )

    reward = {
        "gold": 1_000 * family_level * years,
        "coin": 10 * years,
        "diamond": max(
            1,
            years,
        ),
    }

    return FamilyResult(
        True,
        (
            "🎉 OILA YUBILEYI\n\n"
            f"❤️ Birga o‘tgan yil: {years}\n\n"
            f"🟡 +{reward['gold']:,} oltin\n"
            f"🪙 +{reward['coin']} Coin\n"
            f"💎 +{reward['diamond']} Olmos"
        ),
        reward,
    )


# ============================================================
# FAMILY RANKING SCORE
# ============================================================

def family_ranking_score(
    family: dict,
) -> int:

    level = family.get(
        "level",
        1,
    )

    power = family.get(
        "power",
        0,
    )

    gold = family.get(
        "gold",
        0,
    )

    return (
        level * 100
        + power
        + gold // 100
    )


# ============================================================
# FAMILY RANKING
# ============================================================

def sort_families(
    families: list,
) -> list:

    return sorted(
        families,
        key=family_ranking_score,
        reverse=True,
    )


def family_ranking_text(
    families: list,
) -> str:

    if not families:
        return (
            "❤️ OILA REYTINGI\n\n"
            "Hozircha oilalar mavjud emas."
        )

    families = sort_families(
        families
    )

    lines = [
        "❤️ THRONE OILA REYTINGI",
        "",
    ]

    for index, family in enumerate(
        families[:20],
        start=1,
    ):

        user1 = family.get(
            "user1_id",
            "?",
        )

        user2 = family.get(
            "user2_id",
            "?",
        )

        score = family_ranking_score(
            family
        )

        lines.append(
            f"{index}. ❤️ {user1} × {user2} — ⭐ {score}"
        )

    return "\n".join(lines)


# ============================================================
# DIVORCE PREVIEW
# ============================================================

def divorce_preview(
    family: Optional[dict],
    user_id: int,
) -> FamilyResult:

    if not family:
        return FamilyResult(
            False,
            "❌ Siz nikohda emassiz.",
        )

    if not is_family_member(
        family,
        user_id,
    ):
        return FamilyResult(
            False,
            "❌ Siz ushbu oilaning a’zosi emassiz.",
        )

    partner_id = get_family_partner(
        family,
        user_id,
    )

    return FamilyResult(
        True,
        (
            "💔 NIKOHNI BEKOR QILISH\n\n"
            f"❤️ Turmush o‘rtog‘ingiz: {partner_id}\n\n"
            "⚠️ Bu amal oilaviy statusni yakunlaydi.\n"
            "Tasdiqlash talab qilinadi."
        ),
        {
            "partner_id": partner_id,
            "confirmed": False,
        },
    )


# ============================================================
# FAMILY SERIALIZATION
# ============================================================

def serialize_family(
    family: dict,
) -> dict:

    return {
        "user1_id": family.get(
            "user1_id"
        ),
        "user2_id": family.get(
            "user2_id"
        ),
        "level": family.get(
            "level",
            1,
        ),
        "gold": family.get(
            "gold",
            0,
        ),
        "power": family.get(
            "power",
            0,
        ),
        "status": family.get(
            "status",
            MARRIAGE_ACTIVE,
        ),
        "married_at": family.get(
            "married_at"
        ),
    }


# ============================================================
# FAMILY INFO
# ============================================================

def family_info(
    family: Optional[dict],
    user_id: int,
) -> dict:

    if not family:
        return {
            "married": False,
            "user_id": user_id,
        }

    return {
        "married": is_family_member(
            family,
            user_id,
        ),
        "partner_id": get_family_partner(
            family,
            user_id,
        ),
        "level": family.get(
            "level",
            1,
        ),
        "gold": family.get(
            "gold",
            0,
        ),
        "power": family.get(
            "power",
            0,
        ),
        "status": family.get(
            "status",
            MARRIAGE_ACTIVE,
        ),
      }
