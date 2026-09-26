# ============================================================
# THRONE — DUEL SYSTEM
# ============================================================

from dataclasses import dataclass
from typing import Optional

from config import CREATOR_ID
from database import get_user


# ============================================================
# CONSTANTS
# ============================================================

DUEL_PENDING = "pending"
DUEL_ACCEPTED = "accepted"
DUEL_ACTIVE = "active"
DUEL_FINISHED = "finished"
DUEL_REJECTED = "rejected"
DUEL_CANCELLED = "cancelled"

MIN_HEALTH = 1
BASE_HEALTH = 100

BASE_ATTACK = 10
BASE_DEFENSE = 5

MAX_ROUNDS = 10

DUEL_GOLD_REWARD = 500
DUEL_COIN_REWARD = 5
DUEL_DIAMOND_REWARD = 1


# ============================================================
# RESULT
# ============================================================

@dataclass
class DuelResult:
    success: bool
    message: str
    data: Optional[dict] = None


# ============================================================
# CREATOR
# ============================================================

def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


# ============================================================
# PLAYER STATS
# ============================================================

def player_stats(
    user: Optional[dict],
) -> dict:

    if not user:
        return {
            "level": 1,
            "health": BASE_HEALTH,
            "attack": BASE_ATTACK,
            "defense": BASE_DEFENSE,
        }

    level = max(
        1,
        int(user.get("level", 1) or 1),
    )

    return {
        "level": level,
        "health": BASE_HEALTH + level * 5,
        "attack": BASE_ATTACK + level * 2,
        "defense": BASE_DEFENSE + level,
    }


# ============================================================
# VALIDATE PLAYERS
# ============================================================

async def validate_duel_players(
    challenger_id: int,
    opponent_id: int,
) -> DuelResult:

    if challenger_id == opponent_id:
        return DuelResult(
            False,
            "❌ O‘zingiz bilan duel qila olmaysiz.",
        )

    challenger = await get_user(challenger_id)
    opponent = await get_user(opponent_id)

    if not challenger:
        return DuelResult(
            False,
            "❌ Duel chaqirayotgan o‘yinchi topilmadi.",
        )

    if not opponent:
        return DuelResult(
            False,
            "❌ Raqib topilmadi.",
        )

    return DuelResult(
        True,
        "✅ O‘yinchilar tekshirildi.",
        {
            "challenger": challenger,
            "opponent": opponent,
        },
    )


# ============================================================
# CREATE DUEL
# ============================================================

async def create_duel(
    challenger_id: int,
    opponent_id: int,
) -> DuelResult:

    validation = await validate_duel_players(
        challenger_id,
        opponent_id,
    )

    if not validation.success:
        return validation

    challenger = validation.data["challenger"]
    opponent = validation.data["opponent"]

    challenger_stats = player_stats(
        challenger
    )

    opponent_stats = player_stats(
        opponent
    )

    duel = {
        "challenger_id": challenger_id,
        "opponent_id": opponent_id,
        "status": DUEL_PENDING,
        "round": 0,
        "challenger_health": challenger_stats["health"],
        "opponent_health": opponent_stats["health"],
        "challenger_attack": challenger_stats["attack"],
        "opponent_attack": opponent_stats["attack"],
        "challenger_defense": challenger_stats["defense"],
        "opponent_defense": opponent_stats["defense"],
    }

    return DuelResult(
        True,
        (
            "⚔️ THRONE — DUEL CHAQIRUVI\n\n"
            f"👤 Raqib ID: {opponent_id}\n\n"
            "🏰 Siz raqibni duelga chaqirdingiz.\n"
            "⚔️ Raqib taklifni qabul qilsa, jang boshlanadi."
        ),
        duel,
    )


# ============================================================
# ACCEPT DUEL
# ============================================================

def accept_duel(
    duel: dict,
) -> DuelResult:

    if duel.get("status") != DUEL_PENDING:
        return DuelResult(
            False,
            "❌ Bu duel endi faol emas.",
        )

    duel = dict(duel)

    duel["status"] = DUEL_ACTIVE
    duel["round"] = 1

    return DuelResult(
        True,
        (
            "⚔️ THRONE — DUEL BOSHLANDI\n\n"
            "🏰 Ikki jangchi maydonga chiqdi.\n\n"
            "⚔️ Har bir qaror jang natijasini o‘zgartiradi.\n"
            "🛡️ Hujum va himoyani to‘g‘ri tanlang."
        ),
        duel,
    )


# ============================================================
# REJECT DUEL
# ============================================================

def reject_duel(
    duel: dict,
) -> DuelResult:

    duel = dict(duel)
    duel["status"] = DUEL_REJECTED

    return DuelResult(
        True,
        "❌ Duel taklifi rad etildi.",
        duel,
    )


# ============================================================
# CANCEL DUEL
# ============================================================

def cancel_duel(
    duel: dict,
) -> DuelResult:

    duel = dict(duel)
    duel["status"] = DUEL_CANCELLED

    return DuelResult(
        True,
        "❌ Duel bekor qilindi.",
        duel,
    )


# ============================================================
# DAMAGE
# ============================================================

def calculate_damage(
    attack: int,
    defense: int,
    critical: bool = False,
) -> int:

    attack = max(
        1,
        attack,
    )

    defense = max(
        0,
        defense,
    )

    damage = max(
        1,
        attack - (defense // 2),
    )

    if critical:
        damage *= 2

    return damage


# ============================================================
# ATTACK
# ============================================================

def attack_round(
    duel: dict,
    attacker_id: int,
    critical: bool = False,
) -> DuelResult:

    if duel.get("status") != DUEL_ACTIVE:
        return DuelResult(
            False,
            "❌ Duel faol emas.",
        )

    duel = dict(duel)

    challenger_id = duel.get(
        "challenger_id"
    )

    opponent_id = duel.get(
        "opponent_id"
    )

    if attacker_id == challenger_id:

        damage = calculate_damage(
            duel.get(
                "challenger_attack",
                BASE_ATTACK,
            ),
            duel.get(
                "opponent_defense",
                BASE_DEFENSE,
            ),
            critical,
        )

        duel["opponent_health"] = max(
            MIN_HEALTH,
            duel.get(
                "opponent_health",
                BASE_HEALTH,
            ) - damage,
        )

        target = "opponent"

    elif attacker_id == opponent_id:

        damage = calculate_damage(
            duel.get(
                "opponent_attack",
                BASE_ATTACK,
            ),
            duel.get(
                "challenger_defense",
                BASE_DEFENSE,
            ),
            critical,
        )

        duel["challenger_health"] = max(
            MIN_HEALTH,
            duel.get(
                "challenger_health",
                BASE_HEALTH,
            ) - damage,
        )

        target = "challenger"

    else:
        return DuelResult(
            False,
            "❌ Siz ushbu duel ishtirokchisi emassiz.",
        )

    return DuelResult(
        True,
        (
            "⚔️ HUJUM!\n\n"
            f"💥 Yetkazilgan zarar: {damage}\n"
            f"🎯 Nishon: {target}"
        ),
        {
            "duel": duel,
            "damage": damage,
            "target": target,
            "critical": critical,
        },
    )


# ============================================================
# DEFENSE
# ============================================================

def defense_bonus(
    base_defense: int,
) -> int:

    return max(
        1,
        base_defense // 2,
    )


def defend_round(
    duel: dict,
    player_id: int,
) -> DuelResult:

    if duel.get("status") != DUEL_ACTIVE:
        return DuelResult(
            False,
            "❌ Duel faol emas.",
        )

    duel = dict(duel)

    if player_id == duel.get(
        "challenger_id"
    ):

        bonus = defense_bonus(
            duel.get(
                "challenger_defense",
                BASE_DEFENSE,
            )
        )

        duel["challenger_defense"] += bonus

    elif player_id == duel.get(
        "opponent_id"
    ):

        bonus = defense_bonus(
            duel.get(
                "opponent_defense",
                BASE_DEFENSE,
            )
        )

        duel["opponent_defense"] += bonus

    else:
        return DuelResult(
            False,
            "❌ Siz ushbu duel ishtirokchisi emassiz.",
        )

    return DuelResult(
        True,
        (
            "🛡️ HIMOYA\n\n"
            f"🛡️ Himoya +{bonus}"
        ),
        {
            "duel": duel,
            "defense_bonus": bonus,
        },
    )


# ============================================================
# HEALTH
# ============================================================

def get_duel_health(
    duel: dict,
    player_id: int,
) -> int:

    if player_id == duel.get(
        "challenger_id"
    ):
        return max(
            MIN_HEALTH,
            duel.get(
                "challenger_health",
                BASE_HEALTH,
            ),
        )

    if player_id == duel.get(
        "opponent_id"
    ):
        return max(
            MIN_HEALTH,
            duel.get(
                "opponent_health",
                BASE_HEALTH,
            ),
        )

    return 0


# ============================================================
# CHECK DEFEAT
# ============================================================

def check_defeat(
    duel: dict,
) -> Optional[str]:

    challenger_health = duel.get(
        "challenger_health",
        BASE_HEALTH,
    )

    opponent_health = duel.get(
        "opponent_health",
        BASE_HEALTH,
    )

    if challenger_health <= 0:
        return "challenger"

    if opponent_health <= 0:
        return "opponent"

    return None


# ============================================================
# RESOLVE ROUND
# ============================================================

def resolve_round(
    duel: dict,
) -> DuelResult:

    if duel.get("status") != DUEL_ACTIVE:
        return DuelResult(
            False,
            "❌ Duel faol emas.",
        )

    duel = dict(duel)

    defeated = check_defeat(
        duel
    )

    if defeated:

        if defeated == "challenger":
            winner = "opponent"
        else:
            winner = "challenger"

        duel["status"] = DUEL_FINISHED
        duel["winner"] = winner

        return DuelResult(
            True,
            (
                "🏆 DUEL YAKUNLANDI\n\n"
                f"👑 G‘olib: {winner}\n\n"
                "⚔️ Jang yakunlandi."
            ),
            duel,
        )

    round_number = duel.get(
        "round",
        1,
    )

    if round_number >= MAX_ROUNDS:

        challenger_health = duel.get(
            "challenger_health",
            BASE_HEALTH,
        )

        opponent_health = duel.get(
            "opponent_health",
            BASE_HEALTH,
        )

        if challenger_health > opponent_health:
            winner = "challenger"

        elif opponent_health > challenger_health:
            winner = "opponent"

        else:
            winner = "draw"

        duel["status"] = DUEL_FINISHED
        duel["winner"] = winner

        return DuelResult(
            True,
            (
                "🏆 DUEL YAKUNLANDI\n\n"
                f"👑 Natija: {winner}\n"
                "⏳ Maksimal raund tugadi."
            ),
            duel,
        )

    duel["round"] = round_number + 1

    return DuelResult(
        True,
        (
            "⚔️ KEYINGI RAUND\n\n"
            f"🔢 Raund: {duel['round']}"
        ),
        duel,
    )


# ============================================================
# DUEL REWARD
# ============================================================

def calculate_duel_reward(
    winner_id: int,
    loser_id: int,
    winner_level: int = 1,
) -> dict:

    winner_level = max(
        1,
        winner_level,
    )

    return {
        "winner_id": winner_id,
        "loser_id": loser_id,
        "gold": DUEL_GOLD_REWARD * winner_level,
        "coin": DUEL_COIN_REWARD,
        "diamond": DUEL_DIAMOND_REWARD,
        "rating": 25,
    }


# ============================================================
# DUEL RATING
# ============================================================

def calculate_rating_change(
    winner: str,
) -> dict:

    if winner == "challenger":
        return {
            "challenger": 25,
            "opponent": -10,
        }

    if winner == "opponent":
        return {
            "challenger": -10,
            "opponent": 25,
        }

    return {
        "challenger": 5,
        "opponent": 5,
    }


# ============================================================
# DUEL SUMMARY
# ============================================================

def duel_summary(
    duel: dict,
) -> str:

    challenger_health = duel.get(
        "challenger_health",
        BASE_HEALTH,
    )

    opponent_health = duel.get(
        "opponent_health",
        BASE_HEALTH,
    )

    round_number = duel.get(
        "round",
        1,
    )

    status = duel.get(
        "status",
        DUEL_PENDING,
    )

    status_names = {
        DUEL_PENDING: "⏳ Kutilmoqda",
        DUEL_ACCEPTED: "⚔️ Qabul qilingan",
        DUEL_ACTIVE: "🔥 Faol",
        DUEL_FINISHED: "🏆 Yakunlangan",
        DUEL_REJECTED: "❌ Rad etilgan",
        DUEL_CANCELLED: "❌ Bekor qilingan",
    }

    return (
        "⚔️ THRONE — DUEL\n\n"
        f"👤 {duel.get('challenger_id', '?')}\n"
        f"❤️ HP: {challenger_health}\n\n"
        f"👤 {duel.get('opponent_id', '?')}\n"
        f"❤️ HP: {opponent_health}\n\n"
        f"🔢 Raund: {round_number}\n"
        f"📌 Holat: {status_names.get(status, '❔')}"
    )


# ============================================================
# DUEL RESULT TEXT
# ============================================================

def duel_result_text(
    duel: dict,
) -> str:

    winner = duel.get(
        "winner"
    )

    if winner == "draw":
        return (
            "⚔️ DUEL NATIJASI\n\n"
            "🤝 Durang!\n"
            "Ikki jangchi ham bir xil natija qayd etdi."
        )

    if winner == "challenger":
        winner_id = duel.get(
            "challenger_id"
        )

    elif winner == "opponent":
        winner_id = duel.get(
            "opponent_id"
        )

    else:
        return "⏳ Duel hali yakunlanmagan."

    return (
        "🏆 DUEL NATIJASI\n\n"
        f"👑 G‘olib: {winner_id}\n\n"
        "🟡 Mukofotlar g‘olibga beriladi.\n"
        "📊 Reyting yangilanadi."
    )


# ============================================================
# DUEL HISTORY ITEM
# ============================================================

def duel_history_item(
    duel: dict,
) -> dict:

    return {
        "challenger_id": duel.get(
            "challenger_id"
        ),
        "opponent_id": duel.get(
            "opponent_id"
        ),
        "winner": duel.get(
            "winner"
        ),
        "rounds": duel.get(
            "round",
            0,
        ),
        "status": duel.get(
            "status"
        ),
    }


# ============================================================
# DUEL STATS
# ============================================================

def duel_stats(
    wins: int,
    losses: int,
    draws: int = 0,
) -> dict:

    wins = max(
        0,
        wins,
    )

    losses = max(
        0,
        losses,
    )

    draws = max(
        0,
        draws,
    )

    total = (
        wins
        + losses
        + draws
    )

    win_rate = (
        round(
            wins / total * 100,
            2,
        )
        if total
        else 0
    )

    return {
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "total": total,
        "win_rate": win_rate,
    }


# ============================================================
# DUEL RANKING SCORE
# ============================================================

def duel_ranking_score(
    wins: int,
    losses: int,
    rating: int = 0,
) -> int:

    return (
        max(0, wins) * 100
        - max(0, losses) * 25
        + max(0, rating)
    )


# ============================================================
# DUEL RANKING
# ============================================================

def sort_duel_players(
    players: list,
) -> list:

    return sorted(
        players,
        key=lambda player: duel_ranking_score(
            player.get("wins", 0),
            player.get("losses", 0),
            player.get("rating", 0),
        ),
        reverse=True,
    )


def duel_ranking_text(
    players: list,
) -> str:

    if not players:
        return (
            "⚔️ DUEL REYTINGI\n\n"
            "Hozircha reyting mavjud emas."
        )

    players = sort_duel_players(
        players
    )

    lines = [
        "⚔️ THRONE DUEL REYTINGI",
        "",
    ]

    for index, player in enumerate(
        players[:20],
        start=1,
    ):

        user_id = player.get(
            "user_id",
            "?",
        )

        rating = player.get(
            "rating",
            0,
        )

        wins = player.get(
            "wins",
            0,
        )

        lines.append(
            f"{index}. 👤 {user_id} "
            f"— ⭐ {rating} "
            f"— 🏆 {wins}"
        )

    return "\n".join(lines)


# ============================================================
# FULL DUEL FLOW
# ============================================================

def duel_flow(
    duel: dict,
    action: str,
    player_id: int,
) -> DuelResult:

    action = action.lower().strip()

    if action == "attack":
        return attack_round(
            duel,
            player_id,
        )

    if action == "critical":
        return attack_round(
            duel,
            player_id,
            critical=True,
        )

    if action == "defend":
        return defend_round(
            duel,
            player_id,
        )

    return DuelResult(
        False,
        "❌ Noma’lum duel harakati.",
    )


# ============================================================
# SERIALIZE
# ============================================================

def serialize_duel(
    duel: dict,
) -> dict:

    return {
        "challenger_id": duel.get(
            "challenger_id"
        ),
        "opponent_id": duel.get(
            "opponent_id"
        ),
        "status": duel.get(
            "status"
        ),
        "round": duel.get(
            "round",
            0,
        ),
        "challenger_health": duel.get(
            "challenger_health",
            BASE_HEALTH,
        ),
        "opponent_health": duel.get(
            "opponent_health",
            BASE_HEALTH,
        ),
        "challenger_attack": duel.get(
            "challenger_attack",
            BASE_ATTACK,
        ),
        "opponent_attack": duel.get(
            "opponent_attack",
            BASE_ATTACK,
        ),
        "challenger_defense": duel.get(
            "challenger_defense",
            BASE_DEFENSE,
        ),
        "opponent_defense": duel.get(
            "opponent_defense",
            BASE_DEFENSE,
        ),
        "winner": duel.get(
            "winner"
        ),
      }
