# ============================================================
# THRONE — CLAN SYSTEM
# ============================================================

from dataclasses import dataclass
from typing import Optional

from config import CREATOR_ID
from database import (
    get_user,
    get_kingdom,
)


# ============================================================
# CONSTANTS
# ============================================================

MIN_CLAN_NAME_LENGTH = 3
MAX_CLAN_NAME_LENGTH = 30

MAX_CLAN_LEVEL = 100

BASE_CLAN_LEVEL = 1
BASE_CLAN_POWER = 0
BASE_CLAN_TREASURY = 0

CLAN_CREATE_COST = 1_000
CLAN_LEVEL_COST = 2_500

WAR_PREPARATION_TIME = 60 * 60
WAR_DURATION = 24 * 60 * 60


# ============================================================
# ROLES
# ============================================================

CLAN_LEADER = "leader"
CLAN_COMMANDER = "commander"
CLAN_OFFICER = "officer"
CLAN_MEMBER = "member"


# ============================================================
# RESULT
# ============================================================

@dataclass
class ClanResult:
    success: bool
    message: str
    data: Optional[dict] = None


# ============================================================
# CREATOR
# ============================================================

def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


# ============================================================
# VALIDATE NAME
# ============================================================

def validate_clan_name(name: str) -> ClanResult:

    name = name.strip()

    if len(name) < MIN_CLAN_NAME_LENGTH:
        return ClanResult(
            False,
            f"❌ Klan nomi kamida {MIN_CLAN_NAME_LENGTH} "
            "belgidan iborat bo‘lishi kerak.",
        )

    if len(name) > MAX_CLAN_NAME_LENGTH:
        return ClanResult(
            False,
            f"❌ Klan nomi {MAX_CLAN_NAME_LENGTH} "
            "belgidan oshmasin.",
        )

    return ClanResult(
        True,
        "✅ Klan nomi qabul qilindi.",
        {"name": name},
    )


# ============================================================
# VALIDATE FLAG
# ============================================================

def validate_clan_flag(flag: str) -> ClanResult:

    flag = flag.strip()

    if not flag:
        return ClanResult(
            False,
            "❌ Klan bayrog‘i tanlanmagan.",
        )

    if len(flag) > 8:
        return ClanResult(
            False,
            "❌ Klan bayrog‘i juda uzun.",
        )

    return ClanResult(
        True,
        "✅ Klan bayrog‘i qabul qilindi.",
        {"flag": flag},
    )


# ============================================================
# CLAN STRUCTURE
# ============================================================

def default_clan(
    owner_id: int,
    name: str,
    flag: str = "🏴",
) -> dict:

    return {
        "owner_id": owner_id,
        "name": name,
        "flag": flag,
        "level": BASE_CLAN_LEVEL,
        "power": BASE_CLAN_POWER,
        "treasury": BASE_CLAN_TREASURY,
        "members": 1,
        "leader_id": owner_id,
        "status": "active",
    }


# ============================================================
# MEMBER ROLE
# ============================================================

def role_name(role: str) -> str:

    names = {
        CLAN_LEADER: "👑 Klan rahbari",
        CLAN_COMMANDER: "⚔️ Qo‘mondon",
        CLAN_OFFICER: "🛡️ Ofitser",
        CLAN_MEMBER: "👤 A’zo",
    }

    return names.get(
        role,
        "👤 A’zo",
    )


# ============================================================
# ROLE PERMISSIONS
# ============================================================

def can_manage_clan(role: str) -> bool:

    return role in {
        CLAN_LEADER,
        CLAN_COMMANDER,
    }


def can_manage_members(role: str) -> bool:

    return role in {
        CLAN_LEADER,
        CLAN_COMMANDER,
        CLAN_OFFICER,
    }


def can_start_war(role: str) -> bool:

    return role in {
        CLAN_LEADER,
        CLAN_COMMANDER,
    }


def can_manage_treasury(role: str) -> bool:

    return role in {
        CLAN_LEADER,
        CLAN_COMMANDER,
    }


# ============================================================
# CREATE CLAN DATA
# ============================================================

async def prepare_clan_creation(
    user_id: int,
    name: str,
    flag: str = "🏴",
) -> ClanResult:

    user = await get_user(user_id)

    if not user:
        return ClanResult(
            False,
            "❌ O‘yinchi topilmadi.",
        )

    name_result = validate_clan_name(name)

    if not name_result.success:
        return name_result

    flag_result = validate_clan_flag(flag)

    if not flag_result.success:
        return flag_result

    clan = default_clan(
        user_id,
        name_result.data["name"],
        flag_result.data["flag"],
    )

    return ClanResult(
        True,
        (
            "🏴 KLAN YARATISH\n\n"
            f"{clan['flag']} {clan['name']}\n\n"
            "👑 Siz: Klan rahbari\n"
            f"⭐ Daraja: {clan['level']}\n"
            f"⚔️ Kuch: {clan['power']}\n"
            f"💰 Xazina: {clan['treasury']:,}\n\n"
            f"🟡 Yaratish narxi: {CLAN_CREATE_COST:,} oltin"
        ),
        clan,
    )


# ============================================================
# CLAN LEVEL COST
# ============================================================

def clan_level_cost(level: int) -> int:

    level = max(
        1,
        level,
    )

    return level * CLAN_LEVEL_COST


# ============================================================
# CLAN POWER
# ============================================================

def calculate_clan_power(
    members: int,
    average_level: int = 1,
    army_power: int = 0,
) -> int:

    members = max(
        0,
        members,
    )

    average_level = max(
        1,
        average_level,
    )

    army_power = max(
        0,
        army_power,
    )

    return (
        members * 10
        + average_level * 25
        + army_power
    )


# ============================================================
# CLAN RANKING POINTS
# ============================================================

def calculate_clan_points(
    wins: int,
    wars: int,
    members: int,
) -> int:

    wins = max(
        0,
        wins,
    )

    wars = max(
        0,
        wars,
    )

    members = max(
        0,
        members,
    )

    return (
        wins * 100
        + wars * 10
        + members * 2
    )


# ============================================================
# CLAN WAR POWER
# ============================================================

def calculate_war_power(
    clan_level: int,
    clan_power: int,
    members: int,
) -> int:

    return (
        clan_level * 100
        + clan_power
        + members * 20
    )


# ============================================================
# WAR RESULT
# ============================================================

def calculate_war_result(
    attacker_power: int,
    defender_power: int,
) -> str:

    if attacker_power > defender_power:
        return "attacker"

    if defender_power > attacker_power:
        return "defender"

    return "draw"


# ============================================================
# WAR REWARD
# ============================================================

def calculate_war_reward(
    winning_power: int,
    clan_level: int,
) -> dict:

    winning_power = max(
        0,
        winning_power,
    )

    clan_level = max(
        1,
        clan_level,
    )

    gold = (
        winning_power * 5
        + clan_level * 500
    )

    coin = max(
        10,
        clan_level * 2,
    )

    diamond = max(
        1,
        clan_level // 10,
    )

    return {
        "gold": gold,
        "coin": coin,
        "diamond": diamond,
    }


# ============================================================
# CLAN SUMMARY
# ============================================================

def clan_summary(
    clan: dict,
) -> str:

    name = clan.get(
        "name",
        "Noma’lum klan",
    )

    flag = clan.get(
        "flag",
        "🏴",
    )

    level = clan.get(
        "level",
        1,
    )

    power = clan.get(
        "power",
        0,
    )

    treasury = clan.get(
        "treasury",
        0,
    )

    members = clan.get(
        "members",
        0,
    )

    return (
        "🏴 KLAN\n\n"
        f"{flag} {name}\n\n"
        f"⭐ Daraja: {level}\n"
        f"⚔️ Kuch: {power:,}\n"
        f"👥 A’zolar: {members:,}\n"
        f"💰 Xazina: {treasury:,}"
    )


# ============================================================
# MEMBER SUMMARY
# ============================================================

def member_summary(
    member: dict,
) -> str:

    user_id = member.get(
        "user_id",
        0,
    )

    role = member.get(
        "role",
        CLAN_MEMBER,
    )

    name = member.get(
        "name",
        f"ID {user_id}",
    )

    power = member.get(
        "power",
        0,
    )

    return (
        f"👤 {name}\n"
        f"🆔 ID: {user_id}\n"
        f"🎖️ Lavozim: {role_name(role)}\n"
        f"⚔️ Kuch: {power:,}"
    )


# ============================================================
# CLAN MEMBER LIMIT
# ============================================================

def clan_member_limit(
    clan_level: int,
) -> int:

    clan_level = max(
        1,
        clan_level,
    )

    return 10 + (
        (clan_level - 1) * 5
    )


# ============================================================
# CAN JOIN
# ============================================================

def can_join_clan(
    clan: dict,
    current_members: int,
) -> ClanResult:

    level = clan.get(
        "level",
        1,
    )

    limit = clan_member_limit(
        level
    )

    if current_members >= limit:
        return ClanResult(
            False,
            (
                "❌ Klan to‘la.\n\n"
                f"👥 Limit: {limit}"
            ),
        )

    return ClanResult(
        True,
        "✅ Klan safiga qo‘shilish mumkin.",
        {
            "limit": limit,
        },
    )


# ============================================================
# CAN PROMOTE
# ============================================================

def can_promote(
    actor_role: str,
    target_role: str,
) -> ClanResult:

    if actor_role == CLAN_LEADER:
        return ClanResult(
            True,
            "✅ Ruxsat berildi.",
        )

    if actor_role == CLAN_COMMANDER:
        if target_role == CLAN_MEMBER:
            return ClanResult(
                True,
                "✅ Ruxsat berildi.",
            )

    return ClanResult(
        False,
        "⛔ Sizda bu lavozimni o‘zgartirish huquqi yo‘q.",
    )


# ============================================================
# PROMOTE
# ============================================================

def promote_member(
    actor_role: str,
    target_role: str,
) -> ClanResult:

    permission = can_promote(
        actor_role,
        target_role,
    )

    if not permission.success:
        return permission

    if target_role == CLAN_MEMBER:
        new_role = CLAN_OFFICER

    elif target_role == CLAN_OFFICER:
        new_role = CLAN_COMMANDER

    else:
        return ClanResult(
            False,
            "❌ Bu lavozimni yuqoriga ko‘tarib bo‘lmaydi.",
        )

    return ClanResult(
        True,
        f"🎖️ Yangi lavozim: {role_name(new_role)}",
        {
            "role": new_role,
        },
    )


# ============================================================
# DEMOTE
# ============================================================

def demote_member(
    actor_role: str,
    target_role: str,
) -> ClanResult:

    if actor_role not in {
        CLAN_LEADER,
        CLAN_COMMANDER,
    }:
        return ClanResult(
            False,
            "⛔ Sizda bu huquq mavjud emas.",
        )

    if target_role == CLAN_COMMANDER:
        new_role = CLAN_OFFICER

    elif target_role == CLAN_OFFICER:
        new_role = CLAN_MEMBER

    else:
        return ClanResult(
            False,
            "❌ Bu lavozimni pasaytirib bo‘lmaydi.",
        )

    return ClanResult(
        True,
        f"🎖️ Yangi lavozim: {role_name(new_role)}",
        {
            "role": new_role,
        },
    )


# ============================================================
# CLAN WAR
# ============================================================

def prepare_clan_war(
    attacker: dict,
    defender: dict,
) -> ClanResult:

    attacker_name = attacker.get(
        "name",
        "Hujumchi klan",
    )

    defender_name = defender.get(
        "name",
        "Himoyachi klan",
    )

    attacker_level = attacker.get(
        "level",
        1,
    )

    defender_level = defender.get(
        "level",
        1,
    )

    attacker_power = attacker.get(
        "power",
        0,
    )

    defender_power = defender.get(
        "power",
        0,
    )

    attacker_members = attacker.get(
        "members",
        1,
    )

    defender_members = defender.get(
        "members",
        1,
    )

    attacker_war_power = calculate_war_power(
        attacker_level,
        attacker_power,
        attacker_members,
    )

    defender_war_power = calculate_war_power(
        defender_level,
        defender_power,
        defender_members,
    )

    return ClanResult(
        True,
        (
            "⚔️ KLAN URUSHI\n\n"
            f"🏴 {attacker_name}\n"
            f"⚔️ Kuch: {attacker_war_power:,}\n\n"
            "VS\n\n"
            f"🏴 {defender_name}\n"
            f"🛡️ Kuch: {defender_war_power:,}\n\n"
            "⏳ Urush tayyorlanmoqda..."
        ),
        {
            "attacker": attacker_name,
            "defender": defender_name,
            "attacker_power": attacker_war_power,
            "defender_power": defender_war_power,
            "status": "preparation",
        },
    )


# ============================================================
# RESOLVE CLAN WAR
# ============================================================

def resolve_clan_war(
    attacker: dict,
    defender: dict,
) -> ClanResult:

    attacker_level = attacker.get(
        "level",
        1,
    )

    defender_level = defender.get(
        "level",
        1,
    )

    attacker_power = calculate_war_power(
        attacker_level,
        attacker.get("power", 0),
        attacker.get("members", 1),
    )

    defender_power = calculate_war_power(
        defender_level,
        defender.get("power", 0),
        defender.get("members", 1),
    )

    winner = calculate_war_result(
        attacker_power,
        defender_power,
    )

    if winner == "attacker":
        winner_name = attacker.get(
            "name",
            "Hujumchi",
        )
        winning_power = attacker_power

    elif winner == "defender":
        winner_name = defender.get(
            "name",
            "Himoyachi",
        )
        winning_power = defender_power

    else:
        winner_name = "Durang"
        winning_power = 0

    reward = calculate_war_reward(
        winning_power,
        max(
            attacker_level,
            defender_level,
        ),
    )

    return ClanResult(
        True,
        (
            "🏆 KLAN URUSHI YAKUNI\n\n"
            f"👑 Natija: {winner_name}\n\n"
            f"⚔️ Hujum kuchi: {attacker_power:,}\n"
            f"🛡️ Himoya kuchi: {defender_power:,}\n\n"
            f"🟡 Mukofot: {reward['gold']:,}\n"
            f"🪙 Coin: {reward['coin']}\n"
            f"💎 Olmos: {reward['diamond']}"
        ),
        {
            "winner": winner,
            "winner_name": winner_name,
            "attacker_power": attacker_power,
            "defender_power": defender_power,
            "reward": reward,
        },
    )


# ============================================================
# CLAN RANKING
# ============================================================

def clan_ranking_score(
    clan: dict,
) -> int:

    level = clan.get(
        "level",
        1,
    )

    power = clan.get(
        "power",
        0,
    )

    members = clan.get(
        "members",
        0,
    )

    wins = clan.get(
        "wins",
        0,
    )

    return (
        level * 100
        + power
        + members * 10
        + wins * 200
    )


# ============================================================
# SORT CLANS
# ============================================================

def sort_clans(
    clans: list,
) -> list:

    return sorted(
        clans,
        key=clan_ranking_score,
        reverse=True,
    )


# ============================================================
# CLAN RANKING TEXT
# ============================================================

def clan_ranking_text(
    clans: list,
) -> str:

    if not clans:
        return (
            "🏆 KLAN REYTINGI\n\n"
            "Hozircha klanlar mavjud emas."
        )

    sorted_clans = sort_clans(
        clans
    )

    lines = [
        "🏆 THRONE KLAN REYTINGI",
        "",
    ]

    for index, clan in enumerate(
        sorted_clans[:20],
        start=1,
    ):

        name = clan.get(
            "name",
            "Noma’lum",
        )

        flag = clan.get(
            "flag",
            "🏴",
        )

        score = clan_ranking_score(
            clan
        )

        lines.append(
            f"{index}. {flag} {name} — ⭐ {score}"
        )

    return "\n".join(lines)


# ============================================================
# CLAN WAR STATUS
# ============================================================

def war_status_text(
    war: dict,
) -> str:

    status = war.get(
        "status",
        "unknown",
    )

    statuses = {
        "preparation": "⏳ Tayyorgarlik",
        "active": "⚔️ Urush davom etmoqda",
        "finished": "🏆 Yakunlangan",
        "cancelled": "❌ Bekor qilingan",
    }

    return statuses.get(
        status,
        "❔ Noma’lum",
    )


# ============================================================
# CLAN DASHBOARD
# ============================================================

async def clan_dashboard(
    user_id: int,
) -> ClanResult:

    user = await get_user(user_id)

    if not user:
        return ClanResult(
            False,
            "❌ O‘yinchi topilmadi.",
        )

    kingdom = await get_kingdom(user_id)

    return ClanResult(
        True,
        "🏴 KLAN PANELI",
        {
            "user_id": user_id,
            "kingdom_exists": bool(kingdom),
            "creator": is_creator(user_id),
        },
    )


# ============================================================
# CLAN BENEFITS
# ============================================================

def clan_benefits(
    level: int,
) -> list:

    level = max(
        1,
        level,
    )

    return [
        "🤝 A’zolar uchun bonuslar",
        "⚔️ Klan urushlari",
        "🏆 Klan reytingi",
        "💰 Klan xazinasi",
        "🛡️ Umumiy mudofaa",
        "🎁 Urush mukofotlari",
        f"⭐ Klan darajasi: {level}",
    ]


# ============================================================
# CLAN LEVEL UP
# ============================================================

def level_up_preview(
    current_level: int,
) -> ClanResult:

    if current_level >= MAX_CLAN_LEVEL:
        return ClanResult(
            False,
            "🏆 Klan maksimal darajaga yetgan.",
        )

    cost = clan_level_cost(
        current_level
    )

    return ClanResult(
        True,
        (
            "⬆️ KLAN DARAJASI\n\n"
            f"Joriy: {current_level}\n"
            f"Keyingi: {current_level + 1}\n"
            f"🟡 Narx: {cost:,} oltin"
        ),
        {
            "current_level": current_level,
            "next_level": current_level + 1,
            
