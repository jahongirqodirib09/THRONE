# ============================================================
# THRONE — TOURNAMENT SYSTEM
# ============================================================

from dataclasses import dataclass
from typing import Optional

from config import CREATOR_ID
from database import get_user


# ============================================================
# CONSTANTS
# ============================================================

TOURNAMENT_SOLO = "solo"
TOURNAMENT_CLAN = "clan"
TOURNAMENT_CUP = "throne_cup"

STATUS_REGISTRATION = "registration"
STATUS_ACTIVE = "active"
STATUS_FINISHED = "finished"
STATUS_CANCELLED = "cancelled"

MIN_PLAYERS = 4
MAX_PLAYERS = 64

MAX_ROUNDS = 6

BASE_REWARD_GOLD = 1_000
BASE_REWARD_COIN = 10
BASE_REWARD_DIAMOND = 1

RATING_WIN = 50
RATING_LOSS = -15


# ============================================================
# RESULT
# ============================================================

@dataclass
class TournamentResult:
    success: bool
    message: str
    data: Optional[dict] = None


# ============================================================
# CREATOR
# ============================================================

def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


# ============================================================
# TOURNAMENT TYPES
# ============================================================

def tournament_type_name(
    tournament_type: str,
) -> str:

    names = {
        TOURNAMENT_SOLO: "🏆 Solo Championship",
        TOURNAMENT_CLAN: "🏴 Clan Championship",
        TOURNAMENT_CUP: "👑 THRONE Cup",
    }

    return names.get(
        tournament_type,
        "🏆 Turnir",
    )


# ============================================================
# STATUS
# ============================================================

def tournament_status_name(
    status: str,
) -> str:

    statuses = {
        STATUS_REGISTRATION: "📝 Ro‘yxatdan o‘tish",
        STATUS_ACTIVE: "⚔️ Turnir davom etmoqda",
        STATUS_FINISHED: "🏆 Yakunlangan",
        STATUS_CANCELLED: "❌ Bekor qilingan",
    }

    return statuses.get(
        status,
        "❔ Noma’lum",
    )


# ============================================================
# CREATE TOURNAMENT
# ============================================================

def create_tournament(
    tournament_id: int,
    name: str,
    tournament_type: str = TOURNAMENT_SOLO,
    max_players: int = 16,
) -> TournamentResult:

    if not name.strip():
        return TournamentResult(
            False,
            "❌ Turnir nomi bo‘sh bo‘lishi mumkin emas.",
        )

    max_players = max(
        MIN_PLAYERS,
        min(
            MAX_PLAYERS,
            max_players,
        ),
    )

    if tournament_type not in {
        TOURNAMENT_SOLO,
        TOURNAMENT_CLAN,
        TOURNAMENT_CUP,
    }:
        return TournamentResult(
            False,
            "❌ Turnir turi noto‘g‘ri.",
        )

    tournament = {
        "id": tournament_id,
        "name": name.strip(),
        "type": tournament_type,
        "status": STATUS_REGISTRATION,
        "max_players": max_players,
        "players": [],
        "current_round": 0,
        "max_rounds": MAX_ROUNDS,
        "matches": [],
        "winner_id": None,
    }

    return TournamentResult(
        True,
        (
            "🏆 THRONE — TURNIR YARATILDI\n\n"
            f"👑 {name.strip()}\n"
            f"🎭 Turi: {tournament_type_name(tournament_type)}\n"
            f"👥 Limit: {max_players}\n\n"
            "📝 Ro‘yxatdan o‘tish boshlandi."
        ),
        tournament,
    )


# ============================================================
# ADD PLAYER
# ============================================================

async def join_tournament(
    tournament: dict,
    user_id: int,
) -> TournamentResult:

    if tournament.get("status") != STATUS_REGISTRATION:
        return TournamentResult(
            False,
            "❌ Turnirga qo‘shilish vaqti tugagan.",
        )

    user = await get_user(user_id)

    if not user:
        return TournamentResult(
            False,
            "❌ O‘yinchi topilmadi.",
        )

    tournament = dict(tournament)

    players = list(
        tournament.get(
            "players",
            [],
        )
    )

    if user_id in players:
        return TournamentResult(
            False,
            "❌ Siz allaqachon turnirdasiz.",
        )

    max_players = tournament.get(
        "max_players",
        MAX_PLAYERS,
    )

    if len(players) >= max_players:
        return TournamentResult(
            False,
            "❌ Turnir ishtirokchilari to‘ldi.",
        )

    players.append(user_id)

    tournament["players"] = players

    return TournamentResult(
        True,
        (
            "✅ TURNIRGA QO‘SHILDI\n\n"
            f"👤 O‘yinchi: {user_id}\n"
            f"👥 Ishtirokchilar: {len(players)}/{max_players}"
        ),
        tournament,
    )


# ============================================================
# REMOVE PLAYER
# ============================================================

def leave_tournament(
    tournament: dict,
    user_id: int,
) -> TournamentResult:

    if tournament.get("status") != STATUS_REGISTRATION:
        return TournamentResult(
            False,
            "❌ Turnir boshlanganidan keyin chiqib bo‘lmaydi.",
        )

    tournament = dict(tournament)

    players = list(
        tournament.get(
            "players",
            [],
        )
    )

    if user_id not in players:
        return TournamentResult(
            False,
            "❌ Siz turnir ishtirokchisi emassiz.",
        )

    players.remove(user_id)
    tournament["players"] = players

    return TournamentResult(
        True,
        (
            "🚪 TURNIRDAN CHIQILDI\n\n"
            f"👤 O‘yinchi: {user_id}"
        ),
        tournament,
    )


# ============================================================
# CAN START
# ============================================================

def can_start_tournament(
    tournament: dict,
) -> TournamentResult:

    if tournament.get("status") != STATUS_REGISTRATION:
        return TournamentResult(
            False,
            "❌ Turnir ro‘yxatdan o‘tish holatida emas.",
        )

    players = tournament.get(
        "players",
        [],
    )

    if len(players) < MIN_PLAYERS:
        return TournamentResult(
            False,
            (
                "❌ Ishtirokchilar yetarli emas.\n\n"
                f"👥 Kerak: {MIN_PLAYERS}\n"
                f"👤 Hozir: {len(players)}"
            ),
        )

    return TournamentResult(
        True,
        "✅ Turnirni boshlash mumkin.",
    )


# ============================================================
# BRACKET SIZE
# ============================================================

def next_power_of_two(
    number: int,
) -> int:

    number = max(
        1,
        number,
    )

    power = 1

    while power < number:
        power *= 2

    return power


# ============================================================
# ROUND COUNT
# ============================================================

def calculate_round_count(
    player_count: int,
) -> int:

    size = next_power_of_two(
        player_count
    )

    rounds = 0

    while size > 1:
        size //= 2
        rounds += 1

    return max(
        1,
        rounds,
    )


# ============================================================
# START TOURNAMENT
# ============================================================

def start_tournament(
    tournament: dict,
) -> TournamentResult:

    check = can_start_tournament(
        tournament
    )

    if not check.success:
        return check

    tournament = dict(tournament)

    players = list(
        tournament.get(
            "players",
            [],
        )
    )

    tournament["status"] = STATUS_ACTIVE
    tournament["current_round"] = 1
    tournament["max_rounds"] = calculate_round_count(
        len(players)
    )

    tournament["matches"] = []

    return TournamentResult(
        True,
        (
            "🏆 THRONE — TURNIR BOSHLANDI\n\n"
            f"👥 Ishtirokchilar: {len(players)}\n"
            f"⚔️ Bosqichlar: {tournament['max_rounds']}\n\n"
            "🔥 Birinchi janglar boshlandi!"
        ),
        tournament,
    )


# ============================================================
# CREATE MATCHES
# ============================================================

def create_round_matches(
    tournament: dict,
) -> TournamentResult:

    if tournament.get("status") != STATUS_ACTIVE:
        return TournamentResult(
            False,
            "❌ Turnir faol emas.",
        )

    players = list(
        tournament.get(
            "players",
            [],
        )
    )

    if len(players) < 2:
        return TournamentResult(
            False,
            "❌ Jang uchun o‘yinchilar yetarli emas.",
        )

    matches = []

    index = 0

    while index + 1 < len(players):

        player1 = players[index]
        player2 = players[index + 1]

        matches.append(
            {
                "match_id": len(matches) + 1,
                "player1": player1,
                "player2": player2,
                "winner": None,
                "status": "pending",
            }
        )

        index += 2

    if index < len(players):

        bye_player = players[index]

        matches.append(
            {
                "match_id": len(matches) + 1,
                "player1": bye_player,
                "player2": None,
                "winner": bye_player,
                "status": "bye",
            }
        )

    tournament = dict(tournament)
    tournament["matches"] = matches

    return TournamentResult(
        True,
        (
            "⚔️ JANGLAR JADVALI TAYYOR\n\n"
            f"🥊 Janglar soni: {len(matches)}"
        ),
        tournament,
    )


# ============================================================
# RESOLVE MATCH
# ============================================================

def resolve_match(
    tournament: dict,
    match_id: int,
    winner_id: int,
) -> TournamentResult:

    if tournament.get("status") != STATUS_ACTIVE:
        return TournamentResult(
            False,
            "❌ Turnir faol emas.",
        )

    tournament = dict(tournament)

    matches = [
        dict(match)
        for match in tournament.get(
            "matches",
            [],
        )
    ]

    target = None

    for match in matches:

        if match.get("match_id") == match_id:
            target = match
            break

    if target is None:
        return TournamentResult(
            False,
            "❌ Jang topilmadi.",
        )

    if target.get("status") == "finished":
        return TournamentResult(
            False,
            "❌ Bu jang allaqachon yakunlangan.",
        )

    if winner_id not in {
        target.get("player1"),
        target.get("player2"),
    }:
        return TournamentResult(
            False,
            "❌ G‘olib ushbu jang ishtirokchisi emas.",
        )

    target["winner"] = winner_id
    target["status"] = "finished"

    tournament["matches"] = matches

    return TournamentResult(
        True,
        (
            "🏆 JANG YAKUNLANDI\n\n"
            f"👑 G‘olib: {winner_id}"
        ),
        tournament,
    )


# ============================================================
# ROUND WINNERS
# ============================================================

def get_round_winners(
    tournament: dict,
) -> list:

    winners = []

    for match in tournament.get(
        "matches",
        [],
    ):

        winner = match.get(
            "winner"
        )

        if winner is not None:
            winners.append(
                winner
            )

    return winners


# ============================================================
# CHECK ROUND COMPLETE
# ============================================================

def is_round_complete(
    tournament: dict,
) -> bool:

    matches = tournament.get(
        "matches",
        [],
    )

    if not matches:
        return False

    return all(
        match.get("winner") is not None
        for match in matches
    )


# ============================================================
# NEXT ROUND
# ============================================================

def next_round(
    tournament: dict,
) -> TournamentResult:

    if tournament.get("status") != STATUS_ACTIVE:
        return TournamentResult(
            False,
            "❌ Turnir faol emas.",
        )

    if not is_round_complete(
        tournament
    ):
        return TournamentResult(
            False,
            "⏳ Hali barcha janglar tugamagan.",
        )

    winners = get_round_winners(
        tournament
    )

    tournament = dict(tournament)

    if len(winners) == 1:

        tournament["status"] = STATUS_FINISHED
        tournament["winner_id"] = winners[0]

        return TournamentResult(
            True,
            (
                "👑 THRONE — TURNIR G‘OLIBI\n\n"
                f"🏆 G‘olib: {winners[0]}\n\n"
                "🎁 Mukofotlar hisoblandi."
            ),
            tournament,
        )

    tournament["players"] = winners
    tournament["current_round"] = (
        tournament.get(
            "current_round",
            1,
        ) + 1
    )

    tournament["matches"] = []

    return TournamentResult(
        True,
        (
            "⚔️ KEYINGI BOSQICH\n\n"
            f"🔢 Bosqich: {tournament['current_round']}\n"
            f"👥 Qolgan jangchilar: {len(winners)}"
        ),
        tournament,
    )


# ============================================================
# REWARD
# ============================================================

def calculate_tournament_reward(
    tournament_type: str,
    position: int,
    player_count: int,
) -> dict:

    player_count = max(
        MIN_PLAYERS,
        player_count,
    )

    position = max(
        1,
        position,
    )

    multiplier = {
        TOURNAMENT_SOLO: 1,
        TOURNAMENT_CLAN: 2,
        TOURNAMENT_CUP: 3,
    }.get(
        tournament_type,
        1,
    )

    if position == 1:
        gold = BASE_REWARD_GOLD * 10
        coin = BASE_REWARD_COIN * 10
        diamond = BASE_REWARD_DIAMOND * 10

    elif position == 2:
        gold = BASE_REWARD_GOLD * 6
        coin = BASE_REWARD_COIN * 6
        diamond = BASE_REWARD_DIAMOND * 5

    elif position == 3:
        gold = BASE_REWARD_GOLD * 3
        coin = BASE_REWARD_COIN * 3
        diamond = BASE_REWARD_DIAMOND * 2

    else:
        gold = BASE_REWARD_GOLD
        coin = BASE_REWARD_COIN
        diamond = 0

    return {
        "gold": gold * multiplier,
        "coin": coin * multiplier,
        "diamond": diamond * multiplier,
        "rating": max(
            5,
            100 - (position - 1) * 20,
        ),
        "position": position,
    }


# ============================================================
# WINNER REWARD
# ============================================================

def winner_reward(
    tournament: dict,
) -> dict:

    tournament_type = tournament.get(
        "type",
        TOURNAMENT_SOLO,
    )

    players = tournament.get(
        "players",
        [],
    )

    return calculate_tournament_reward(
        tournament_type,
        1,
        len(players),
    )


# ============================================================
# RATING
# ============================================================

def tournament_rating_change(
    position: int,
) -> int:

    if position == 1:
        return 100

    if position == 2:
        return 60

    if position == 3:
        return 40

    return max(
        5,
        25 - position,
    )


# ============================================================
# TOURNAMENT SUMMARY
# ============================================================

def tournament_summary(
    tournament: dict,
) -> str:

    name = tournament.get(
        "name",
        "THRONE Turniri",
    )

    tournament_type = tournament.get(
        "type",
        TOURNAMENT_SOLO,
    )

    status = tournament.get(
        "status",
        STATUS_REGISTRATION,
    )

    players = tournament.get(
        "players",
        [],
    )

    current_round = tournament.get(
        "current_round",
        0,
    )

    max_rounds = tournament.get(
        "max_rounds",
        0,
    )

    return (
        "🏆 THRONE — TURNIR\n\n"
        f"👑 {name}\n"
        f"🎭 {tournament_type_name(tournament_type)}\n"
        f"📌 {tournament_status_name(status)}\n\n"
        f"👥 Ishtirokchilar: {len(players)}"
        f"/{tournament.get('max_players', MAX_PLAYERS)}\n"
        f"⚔️ Bosqich: {current_round}/{max_rounds}"
    )


# ============================================================
# TOURNAMENT RANKING
# ============================================================

def tournament_ranking_score(
    wins: int,
    tournaments: int,
    rating: int = 0,
) -> int:

    return (
        max(0, wins) * 100
        + max(0, tournaments) * 25
        + max(0, rating)
    )


def sort_tournament_players(
    players: list,
) -> list:

    return sorted(
        players,
        key=lambda player: tournament_ranking_score(
            player.get("wins", 0),
            player.get("tournaments", 0),
            player.get("rating", 0),
        ),
        reverse=True,
    )


def tournament_ranking_text(
    players: list,
) -> str:

    if not players:
        return (
            "🏆 TURNIR REYTINGI\n\n"
            "Hozircha reyting mavjud emas."
        )

    players = sort_tournament_players(
        players
    )

    lines = [
        "🏆 THRONE TURNIR REYTINGI",
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
# TOURNAMENT RESULT
# ============================================================

def tournament_result_text(
    tournament: dict,
) -> str:

    winner_id = tournament.get(
        "winner_id"
    )

    if winner_id is None:
        return (
            "⏳ Turnir hali yakunlanmagan."
        )

    reward = winner_reward(
        tournament
    )

    return (
        "👑 THRONE — TURNIR NATIJASI\n\n"
        f"🏆 G‘olib: {winner_id}\n\n"
        f"🟡 Oltin: +{reward['gold']:,}\n"
        f"🪙 Coin: +{reward['coin']}\n"
        f"💎 Olmos: +{reward['diamond']}\n"
        f"⭐ Reyting: +{reward['rating']}"
    )


# ============================================================
# CANCEL TOURNAMENT
# ============================================================

def cancel_tournament(
    tournament: dict,
    reason: str = "Administrator tomonidan bekor qilindi.",
) -> TournamentResult:

    if tournament.get("status") == STATUS_FINISHED:
        return TournamentResult(
            False,
            "❌ Yakunlangan turnirni bekor qilib bo‘lmaydi.",
        )

    tournament = dict(tournament)

    tournament["status"] = STATUS_CANCELLED

    return TournamentResult(
        True,
        (
            "❌ TURNIR BEKOR QILINDI\n\n"
            f"📌 Sabab: {reason}"
        ),
        tournament,
    )


# ============================================================
# SERIALIZE
# ============================================================

def serialize_tournament(
    tournament: dict,
) -> dict:

    return {
        "id": tournament.get("id"),
        "name": tournament.get("name"),
        "type": tournament.get(
  
