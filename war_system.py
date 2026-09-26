from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta


# ============================================================
# THRONE — WAR SYSTEM
# ============================================================

WAR_PREPARATION_HOURS = 6
WAR_MAX_ROUNDS = 10

WAR_STATUS_DECLARED = "declared"
WAR_STATUS_PREPARATION = "preparation"
WAR_STATUS_ACTIVE = "active"
WAR_STATUS_FINISHED = "finished"
WAR_STATUS_CANCELLED = "cancelled"


@dataclass
class WarResult:
    success: bool
    message: str = ""
    war_id: Optional[str] = None
    data: Optional[dict] = None


# ============================================================
# BASIC HELPERS
# ============================================================

def now() -> datetime:
    return datetime.utcnow()


def create_war_id(
    attacker_id: int,
    defender_id: int,
) -> str:
    timestamp = int(now().timestamp())

    return (
        f"WAR-{attacker_id}-"
        f"{defender_id}-{timestamp}"
    )


def calculate_war_power(
    army_power: int = 0,
    kingdom_power: int = 0,
    territory_power: int = 0,
    commander_bonus: int = 0,
    defense_bonus: int = 0,
) -> int:

    army_power = max(0, int(army_power))
    kingdom_power = max(0, int(kingdom_power))
    territory_power = max(0, int(territory_power))
    commander_bonus = max(0, int(commander_bonus))
    defense_bonus = max(0, int(defense_bonus))

    return (
        army_power
        + kingdom_power
        + territory_power
        + commander_bonus
        + defense_bonus
    )


# ============================================================
# WAR CREATION
# ============================================================

def declare_war(
    attacker_id: int,
    defender_id: int,
    territory_id: Optional[str] = None,
) -> WarResult:

    if not attacker_id:
        return WarResult(
            success=False,
            message="❌ Hujumchi qirollik aniqlanmadi.",
        )

    if not defender_id:
        return WarResult(
            success=False,
            message="❌ Himoyachi qirollik aniqlanmadi.",
        )

    if attacker_id == defender_id:
        return WarResult(
            success=False,
            message="❌ O‘z qirolligingizga urush e’lon qila olmaysiz.",
        )

    war_id = create_war_id(
        attacker_id,
        defender_id,
    )

    preparation_until = (
        now()
        + timedelta(
            hours=WAR_PREPARATION_HOURS
        )
    )

    war = {
        "war_id": war_id,
        "attacker_id": attacker_id,
        "defender_id": defender_id,
        "territory_id": territory_id,
        "status": WAR_STATUS_DECLARED,
        "round": 0,
        "attacker_power": 0,
        "defender_power": 0,
        "attacker_losses": 0,
        "defender_losses": 0,
        "preparation_until": preparation_until.isoformat(),
        "started_at": None,
        "finished_at": None,
        "winner_id": None,
        "loser_id": None,
        "reward": 0,
    }

    return WarResult(
        success=True,
        war_id=war_id,
        message=(
            "⚔️ URUSH E’LON QILINDI!\n\n"
            f"👑 Hujumchi: {attacker_id}\n"
            f"🏰 Himoyachi: {defender_id}\n\n"
            f"⏳ Tayyorgarlik: "
            f"{WAR_PREPARATION_HOURS} soat"
        ),
        data=war,
    )


# ============================================================
# PREPARATION
# ============================================================

def start_preparation(
    war: dict,
) -> WarResult:

    if not war:
        return WarResult(
            success=False,
            message="❌ Urush topilmadi.",
        )

    status = war.get("status")

    if status not in (
        WAR_STATUS_DECLARED,
        WAR_STATUS_PREPARATION,
    ):
        return WarResult(
            success=False,
            message="❌ Urush tayyorgarlik bosqichida emas.",
        )

    war["status"] = WAR_STATUS_PREPARATION

    if not war.get("preparation_until"):
        war["preparation_until"] = (
            now()
            + timedelta(
                hours=WAR_PREPARATION_HOURS
            )
        ).isoformat()

    return WarResult(
        success=True,
        war_id=war.get("war_id"),
        message=(
            "🛡️ Urushga tayyorgarlik boshlandi.\n\n"
            "⚔️ Qo‘shinlarni tayyorlang.\n"
            "🏰 Mudofaani kuchaytiring.\n"
            "👑 Strategiyani belgilang."
        ),
        data=war,
    )


def is_preparation_finished(
    war: dict,
) -> bool:

    if not war:
        return False

    value = war.get(
        "preparation_until"
    )

    if not value:
        return True

    try:
        deadline = datetime.fromisoformat(
            value
        )
        return now() >= deadline
    except (
        ValueError,
        TypeError,
    ):
        return True


def can_start_war(
    war: dict,
) -> WarResult:

    if not war:
        return WarResult(
            success=False,
            message="❌ Urush topilmadi.",
        )

    if war.get("status") == WAR_STATUS_FINISHED:
        return WarResult(
            success=False,
            message="❌ Urush allaqachon tugagan.",
        )

    if war.get("status") == WAR_STATUS_CANCELLED:
        return WarResult(
            success=False,
            message="❌ Urush bekor qilingan.",
        )

    if not is_preparation_finished(war):
        return WarResult(
            success=False,
            message="⏳ Urush hali tayyorgarlik bosqichida.",
        )

    return WarResult(
        success=True,
        war_id=war.get("war_id"),
        message="⚔️ Urushni boshlash mumkin.",
    )


# ============================================================
# POWER
# ============================================================

def set_war_power(
    war: dict,
    attacker_power: int,
    defender_power: int,
) -> WarResult:

    if not war:
        return WarResult(
            success=False,
            message="❌ Urush topilmadi.",
        )

    attacker_power = max(
        0,
        int(attacker_power),
    )

    defender_power = max(
        0,
        int(defender_power),
    )

    war["attacker_power"] = attacker_power
    war["defender_power"] = defender_power

    return WarResult(
        success=True,
        war_id=war.get("war_id"),
        message="⚔️ Urush kuchlari belgilandi.",
        data={
            "attacker_power": attacker_power,
            "defender_power": defender_power,
        },
    )


# ============================================================
# START WAR
# ============================================================

def start_war(
    war: dict,
) -> WarResult:

    check = can_start_war(war)

    if not check.success:
        return check

    war["status"] = WAR_STATUS_ACTIVE
    war["started_at"] = now().isoformat()
    war["round"] = 1

    return WarResult(
        success=True,
        war_id=war.get("war_id"),
        message=(
            "⚔️ URUSH BOSHLANDI!\n\n"
            "🏰 Ikki qirollik qo‘shini maydonga chiqdi.\n"
            "🛡️ Himoya saf tortdi.\n"
            "⚔️ Hujum boshlandi."
        ),
        data=war,
    )


# ============================================================
# ROUND SYSTEM
# ============================================================

def calculate_round_damage(
    attacker_power: int,
    defender_power: int,
) -> dict:

    attacker_power = max(
        0,
        int(attacker_power),
    )

    defender_power = max(
        0,
        int(defender_power),
    )

    if attacker_power == 0:
        attacker_damage = 0
    else:
        attacker_damage = max(
            1,
            int(
                attacker_power * 0.15
            ),
        )

    if defender_power == 0:
        defender_damage = 0
    else:
        defender_damage = max(
            1,
            int(
                defender_power * 0.12
            ),
        )

    return {
        "attacker_damage": attacker_damage,
        "defender_damage": defender_damage,
    }


def resolve_round(
    war: dict,
) -> WarResult:

    if not war:
        return WarResult(
            success=False,
            message="❌ Urush topilmadi.",
        )

    if war.get("status") != WAR_STATUS_ACTIVE:
        return WarResult(
            success=False,
            message="❌ Faol urush mavjud emas.",
        )

    attacker_power = max(
        0,
        int(war.get(
            "attacker_power",
            0,
        )),
    )

    defender_power = max(
        0,
        int(war.get(
            "defender_power",
            0,
        )),
    )

    if attacker_power <= 0 and defender_power <= 0:
        return finish_war(
            war,
            winner_id=None,
            loser_id=None,
            reason="Ikki tomon ham jangovar kuchsiz qoldi.",
        )

    damage = calculate_round_damage(
        attacker_power,
        defender_power,
    )

    attacker_losses = damage[
        "defender_damage"
    ]

    defender_losses = damage[
        "attacker_damage"
    ]

    war["attacker_power"] = max(
        0,
        attacker_power - attacker_losses,
    )

    war["defender_power"] = max(
        0,
        defender_power - defender_losses,
    )

    war["attacker_losses"] += attacker_losses
    war["defender_losses"] += defender_losses

    current_round = int(
        war.get("round", 1)
    )

    war["round"] = current_round + 1

    if war["defender_power"] <= 0:
        return finish_war(
            war,
            winner_id=war.get("attacker_id"),
            loser_id=war.get("defender_id"),
            reason="Himoya qo‘shini mag‘lub bo‘ldi.",
        )

    if war["attacker_power"] <= 0:
        return finish_war(
            war,
            winner_id=war.get("defender_id"),
            loser_id=war.get("attacker_id"),
            reason="Hujumchi qo‘shin mag‘lub bo‘ldi.",
        )

    if current_round >= WAR_MAX_ROUNDS:
        if (
            war["attacker_power"]
            > war["defender_power"]
        ):
            winner_id = war.get(
                "attacker_id"
            )
            loser_id = war.get(
                "defender_id"
            )

        elif (
            war["defender_power"]
            > war["attacker_power"]
        ):
            winner_id = war.get(
                "defender_id"
            )
            loser_id = war.get(
                "attacker_id"
            )

        else:
            winner_id = None
            loser_id = None

        return finish_war(
            war,
            winner_id=winner_id,
            loser_id=loser_id,
            reason="Maksimal jang raundlari tugadi.",
        )

    return WarResult(
        success=True,
        war_id=war.get("war_id"),
        message=(
            f"⚔️ {current_round}-raund yakunlandi.\n\n"
            f"👑 Hujumchi kuchi: "
            f"{war['attacker_power']}\n"
            f"🏰 Himoyachi kuchi: "
            f"{war['defender_power']}"
        ),
        data={
            "round": current_round,
            "attacker_power": war[
                "attacker_power"
            ],
            "defender_power": war[
                "defender_power"
            ],
            "attacker_losses": attacker_losses,
            "defender_losses": defender_losses,
        },
    )


def resolve_all_rounds(
    war: dict,
) -> WarResult:

    if not war:
        return WarResult(
            success=False,
            message="❌ Urush topilmadi.",
        )

    result = None

    for _ in range(WAR_MAX_ROUNDS):

        if war.get("status") != WAR_STATUS_ACTIVE:
            break

        result = resolve_round(war)

        if not result.success:
            return result

        if war.get("status") == WAR_STATUS_FINISHED:
            return result

    if war.get("status") == WAR_STATUS_ACTIVE:
        return finish_war(
            war,
            winner_id=None,
            loser_id=None,
            reason="Urush durang bilan yakunlandi.",
        )

    return result or WarResult(
        success=False,
        message="❌ Urush natijasi olinmadi.",
    )


# ============================================================
# REWARDS
# ============================================================

def calculate_war_reward(
    war: dict,
) -> int:

    if not war:
        return 0

    attacker_power = int(
        war.get(
            "attacker_power",
            0,
        )
    )

    defender_power = int(
        war.get(
            "defender_power",
            0,
        )
    )

    total_power = (
        attacker_power
        + defender_power
        + int(
            war.get(
                "attacker_losses",
                0,
            )
        )
        + int(
            war.get(
                "defender_losses",
                0,
            )
        )
    )

    return max(
        100,
        total_power // 2,
    )


def apply_war_reward(
    war: dict,
) -> WarResult:

    if not war:
        return WarResult(
            success=False,
            message="❌ Urush topilmadi.",
        )

    winner_id = war.get(
        "winner_id"
    )

    if not winner_id:
        return WarResult(
            success=False,
            message="⚖️ G‘olib aniqlanmagan. Mukofot berilmaydi.",
        )

    reward = calculate_war_reward(
        war
    )

    war["reward"] = reward

    return WarResult(
        success=True,
        war_id=war.get("war_id"),
        message=(
            f"🎁 Urush mukofoti: "
            f"{reward} oltin."
        ),
        data={
            "winner_id": winner_id,
            "reward": reward,
        },
    )


# ============================================================
# FINISH / CANCEL
# ============================================================

def finish_war(
    war: dict,
    winner_id: Optional[int],
    loser_id: Optional[int],
    reason: str = "",
) -> WarResult:

    if not war:
        return WarResult(
            success=False,
            message="❌ Urush topilmadi.",
        )

    war["status"] = WAR_STATUS_FINISHED
    war["winner_id"] = winner_id
    war["loser_id"] = loser_id
    war["finished_at"] = now().isoformat()

    if winner_id:
        result_message = (
            "🏆 URUSH YAKUNLANDI!\n\n"
            f"👑 G‘olib: {winner_id}\n"
            f"💀 Mag‘lub: {loser_id}\n\n"
            f"📜 {reason}"
        )
    else:
        result_message = (
            "⚖️ URUSH YAKUNLANDI!\n\n"
            "Natija: DURANG\n\n"
            f"📜 {reason}"
        )

    return WarResult(
        success=True,
        war_id=war.get("war_id"),
        message=result_message,
        data={
            "winner_id": winner_id,
            "loser_id": loser_id,
            "reason": reason,
        },
    )


def cancel_war(
    war: dict,
    reason: str = "Urush bekor qilindi.",
) -> WarResult:

    if not war:
        return WarResult(
            success=False,
            message="❌ Urush topilmadi.",
        )

    if war.get("status") == WAR_STATUS_FINISHED:
        return WarResult(
            success=False,
            message="❌ Tugagan urushni bekor qilib bo‘lmaydi.",
        )

    war["status"] = WAR_STATUS_CANCELLED
    war["finished_at"] = now().isoformat()

    return WarResult(
        success=True,
        war_id=war.get("war_id"),
        message=(
            "🛑 URUSH BEKOR QILINDI\n\n"
            f"📜 Sabab: {reason}"
        ),
        data={
            "reason": reason,
        },
    )


# ============================================================
# WAR STATUS
# ============================================================

def get_war_status_text(
    war: dict,
) -> str:

    if not war:
        return "❌ Urush topilmadi."

    status = war.get(
        "status",
        WAR_STATUS_DECLARED,
    )

    status_names = {
        WAR_STATUS_DECLARED: "📜 E’LON QILINGAN",
        WAR_STATUS_PREPARATION: "🛡️ TAYYORGARLIK",
        WAR_STATUS_ACTIVE: "⚔️ FAOL URUSH",
        WAR_STATUS_FINISHED: "🏆 YAKUNLANGAN",
        WAR_STATUS_CANCELLED: "🛑 BEKOR QILINGAN",
    }

    status_text = status_names.get(
        status,
        "❓ NOMA’LUM",
    )

    return (
        f"⚔️ URUSH HOLATI\n\n"
        f"🆔 {war.get('war_id')}\n"
        f"👑 Hujumchi: {war.get('attacker_id')}\n"
        f"🏰 Himoyachi: {war.get('defender_id')}\n"
        f"📊 Holat: {status_text}\n"
        f"🔢 Raund: {war.get('round', 0)}\n\n"
        f"⚔️ Hujumchi kuchi: "
        f"{war.get('attacker_power', 0)}\n"
        f"🛡️ Himoyachi kuchi: "
        f"{war.get('defender_power', 0)}\n\n"
        f"💀 Hujumchi yo‘qotishi: "
        f"{war.get('attacker_losses', 0)}\n"
        f"💀 Himoyachi yo‘qotishi: "
        f"{war.get('defender_losses', 0)}"
    )


# ============================================================
# WAR SUMMARY
# ============================================================

def war_summary(
    war: dict,
) -> dict:

    if not war:
        return {}

    return {
        "war_id": war.get("war_id"),
        "attacker_id": war.get("attacker_id"),
        "defender_id": war.get("defender_id"),
        "territory_id": war.get("territory_id"),
        "status": war.get("status"),
        "round": war.get("round", 0),
        "attacker_power": war.get(
            "attacker_power",
            0,
        ),
        "defender_power": war.get(
            "defender_power",
            0,
        ),
        "attacker_losses": war.get(
            "attacker_losses",
            0,
        ),
        "defender_losses": war.get(
            "defender_losses",
            0,
        ),
        "winner_id": war.get(
            "winner_id"
        ),
        "loser_id": war.get(
            "loser_id"
        ),
        "reward": war.get(
            "reward",
            0,
        ),
    }


def serialize_war(
    war: dict,
) -> dict:

    if not war:
        return {}

    return dict(
        war
    )


# ============================================================
# WAR HISTORY / RANKING HELPERS
# ============================================================

def get_winner(
    war: dict,
) -> Optional[int]:

    if not war:
        return None

    return war.get(
        "winner_id"
    )


def get_loser(
    war: dict,
) -> Optional[int]:

    if not war:
        return None

    return war.get(
        "loser_id"
    )


def is_war_active(
    war: dict,
) -> bool:

    if not war:
        return False

    return war.get(
        "status"
    ) == WAR_STATUS_ACTIVE


def is_war_finished(
    war: dict,
) -> bool:

    if not war:
        return False

    return war.get(
        "status"
    ) == WAR_STATUS_FINISHED


def calculate_war_score(
    wars: List[dict],
    user_id: int,
) -> int:

    score = 0

    for war in wars:

        if war.get("winner_id") == user_id:
            score += 100

        elif war.get("loser_id") == user_id:
            score += 20

    return score


def war_ranking(
    wars: List[dict],
) -> List[dict]:

    users = set()

    for war in wars:

        attacker_id = war.get(
            "attacker_id"
        )

        defender_id = war.get(
            "defender_id"
        )

        if attacker_id:
            users.add(attacker_id)

        if defender_id:
            users.add(defender_id)

    ranking = []

    for user_id in users:

        score = calculate_war_score(
            wars,
            user_id,
        )

        wins = sum(
            1
            for war in wars
            if war.get("winner_id")
            == user_id
        )

        losses = sum(
            1
            for war in wars
            if war.get("loser_id")
            == user_id
        )

        ranking.append(
            {
                "user_id": user_id,
                "score": score,
                "wins": wins,
                "losses": losses,
            }
        )

    ranking.sort(
        key=lambda item: (
            item["score"],
     
