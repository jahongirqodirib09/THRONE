# ============================================================
# THRONE — GAME VICTORY
# ============================================================

from dataclasses import dataclass
from typing import Dict, List, Optional

from game_state import (
    GameState,
    get_alive_players,
)


# ============================================================
# SIDES
# ============================================================

SIDE_TAXT = "Taxt"
SIDE_QORA = "Qora"
SIDE_ISYON = "Isyon"
SIDE_MUSTAQIL = "Mustaqil"


# ============================================================
# VICTORY STATUS
# ============================================================

STATUS_CONTINUE = "continue"
STATUS_TAXT = "taxt_win"
STATUS_QORA = "qora_win"
STATUS_ISYON = "isyon_win"
STATUS_MUSTAQIL = "mustaqil_win"


@dataclass
class VictoryResult:
    finished: bool
    winner: Optional[str] = None
    winners: List[int] = None
    reason: str = ""
    alive_by_side: Dict[str, int] = None

    def __post_init__(self):
        if self.winners is None:
            self.winners = []

        if self.alive_by_side is None:
            self.alive_by_side = {}


# ============================================================
# ALIVE PLAYERS BY SIDE
# ============================================================

def get_alive_by_side(
    state: GameState,
) -> Dict[str, List[int]]:

    result = {
        SIDE_TAXT: [],
        SIDE_QORA: [],
        SIDE_ISYON: [],
        SIDE_MUSTAQIL: [],
    }

    for player in get_alive_players(state):

        side = getattr(
            player,
            "side",
            None,
        )

        if side not in result:
            result[side] = []

        result[side].append(
            player.user_id
        )

    return result


# ============================================================
# ALIVE COUNTS
# ============================================================

def get_alive_counts(
    state: GameState,
) -> Dict[str, int]:

    alive = get_alive_by_side(
        state
    )

    return {
        side: len(players)
        for side, players in alive.items()
    }


# ============================================================
# SIDE ALIVE CHECK
# ============================================================

def side_alive(
    state: GameState,
    side: str,
) -> bool:

    alive = get_alive_by_side(
        state
    )

    return bool(
        alive.get(side, [])
    )


# ============================================================
# TOTAL ALIVE
# ============================================================

def total_alive(
    state: GameState,
) -> int:

    return len(
        get_alive_players(state)
    )


# ============================================================
# TAHT VICTORY
# ============================================================

def check_taxt_victory(
    state: GameState,
) -> bool:

    taxt_alive = side_alive(
        state,
        SIDE_TAXT,
    )

    qora_alive = side_alive(
        state,
        SIDE_QORA,
    )

    isyon_alive = side_alive(
        state,
        SIDE_ISYON,
    )

    if not taxt_alive:
        return False

    # Taxt tomoni qora va isyon xavfini
    # to'liq yo'q qilganida g'alaba.
    if not qora_alive and not isyon_alive:
        return True

    return False


# ============================================================
# QORA VICTORY
# ============================================================

def check_qora_victory(
    state: GameState,
) -> bool:

    qora = side_alive(
        state,
        SIDE_QORA,
    )

    if not qora:
        return False

    taxt_count = len(
        get_alive_by_side(state).get(
            SIDE_TAXT,
            [],
        )
    )

    isyon_count = len(
        get_alive_by_side(state).get(
            SIDE_ISYON,
            [],
        )
    )

    qora_count = len(
        get_alive_by_side(state).get(
            SIDE_QORA,
            [],
        )
    )

    active_enemy_count = (
        taxt_count + isyon_count
    )

    # Qora tomon qolgan faol dushmanlardan
    # son jihatdan ustun yoki teng bo'lsa,
    # qirollik ustidan nazorat o'rnatiladi.
    if active_enemy_count <= qora_count:
        return True

    return False


# ============================================================
# ISYON VICTORY
# ============================================================

def check_isyon_victory(
    state: GameState,
) -> bool:

    isyon = side_alive(
        state,
        SIDE_ISYON,
    )

    if not isyon:
        return False

    taxt_count = len(
        get_alive_by_side(state).get(
            SIDE_TAXT,
            [],
        )
    )

    qora_count = len(
        get_alive_by_side(state).get(
            SIDE_QORA,
            [],
        )
    )

    isyon_count = len(
        get_alive_by_side(state).get(
            SIDE_ISYON,
            [],
        )
    )

    active_enemy_count = (
        taxt_count + qora_count
    )

    if active_enemy_count <= isyon_count:
        return True

    return False


# ============================================================
# INDEPENDENT VICTORY
# ============================================================

def check_independent_victory(
    state: GameState,
) -> Optional[str]:

    alive = get_alive_by_side(
        state
    )

    independent_players = alive.get(
        SIDE_MUSTAQIL,
        [],
    )

    if not independent_players:
        return None

    # Mustaqil rollarning aniq g'alaba sharti
    # keyinchalik role-specific qoidalar orqali
    # tekshiriladi.
    #
    # Hozircha ular oddiy faction victory'ni
    # avtomatik bekor qilmaydi.
    return None


# ============================================================
# CHECK VICTORY
# ============================================================

def check_victory(
    state: GameState,
) -> VictoryResult:

    alive = get_alive_by_side(
        state
    )

    counts = {
        side: len(players)
        for side, players in alive.items()
    }

    # --------------------------------------------------------
    # Mustaqil rollar
    # --------------------------------------------------------

    independent_winner = (
        check_independent_victory(state)
    )

    if independent_winner:

        winners = alive.get(
            SIDE_MUSTAQIL,
            [],
        )

        return VictoryResult(
            finished=True,
            winner=independent_winner,
            winners=winners,
            reason=(
                "Mustaqil o'yinchining "
                "maxsus g'alaba sharti bajarildi."
            ),
            alive_by_side=counts,
        )

    # --------------------------------------------------------
    # Taxt
    # --------------------------------------------------------

    if check_taxt_victory(state):

        winners = alive.get(
            SIDE_TAXT,
            [],
        )

        return VictoryResult(
            finished=True,
            winner=STATUS_TAXT,
            winners=winners,
            reason=(
                "Taxt tomoni Qora va Isyon "
                "kuchlarini yo'q qildi."
            ),
            alive_by_side=counts,
        )

    # --------------------------------------------------------
    # Qora
    # --------------------------------------------------------

    if check_qora_victory(state):

        winners = alive.get(
            SIDE_QORA,
            [],
        )

        return VictoryResult(
            finished=True,
            winner=STATUS_QORA,
            winners=winners,
            reason=(
                "Qora tomon qirollik ustidan "
                "nazorat o'rnatdi."
            ),
            alive_by_side=counts,
        )

    # --------------------------------------------------------
    # Isyon
    # --------------------------------------------------------

    if check_isyon_victory(state):

        winners = alive.get(
            SIDE_ISYON,
            [],
        )

        return VictoryResult(
            finished=True,
            winner=STATUS_ISYON,
            winners=winners,
            reason=(
                "Isyonchilar hokimiyatni "
                "egallash uchun yetarli kuchga ega bo'ldi."
            ),
            alive_by_side=counts,
        )

    # --------------------------------------------------------
    # O'YIN DAVOM ETADI
    # --------------------------------------------------------

    return VictoryResult(
        finished=False,
        winner=None,
        winners=[],
        reason="O'yin davom etmoqda.",
        alive_by_side=counts,
    )


# ============================================================
# WINNER MESSAGE
# ============================================================

def get_victory_message(
    result: VictoryResult,
) -> str:

    if not result.finished:
        return (
            "⚔️ THRONE davom etmoqda.\n\n"
            "👑 Taxt uchun kurash hali tugamadi."
        )

    if result.winner == STATUS_TAXT:

        return (
            "👑 THRONE — G'ALABA\n\n"
            "🏰 TAХT TOMONI G'ALABA QOZONDI!\n\n"
            "⚔️ Qirollik dushman kuchlaridan "
            "tozalandi.\n"
            "👑 Taxt saqlab qolindi."
        )

    if result.winner == STATUS_QORA:

        return (
            "🩸 THRONE — G'ALABA\n\n"
            "🩸 QORA TOMON G'ALABA QOZONDI!\n\n"
            "🌑 Qirollik ustidan qorong'u "
            "hukmronlik o'rnatildi."
        )

    if result.winner == STATUS_ISYON:

        return (
            "🏴 THRONE — G'ALABA\n\n"
            "⚔️ ISYON TOMONI G'ALABA QOZONDI!\n\n"
            "🔥 Eski tartib qulab tushdi.\n"
            "🏰 Qirollik taqdiri o'zgardi."
        )

    if result.winner == STATUS_MUSTAQIL:

        return (
            "🃏 THRONE — MAXSUS G'ALABA\n\n"
            "☠️ MUSTAQIL O'YINCHI "
            "O'Z MAQSADIGA ERISHDI!"
        )

    return (
        "👑 THRONE yakunlandi.\n\n"
        "⚔️ O'yin natijasi aniqlandi."
    )


# ============================================================
# WINNER DETAILS
# ============================================================

def get_winner_details(
    state: GameState,
    result: VictoryResult,
) -> Dict:

    alive = get_alive_by_side(
        state
    )

    return {
        "winner": result.winner,
        "winners": list(
            result.winners
        ),
        "reason": result.reason,
        "alive_players": {
            side: list(players)
            for side, players in alive.items()
        },
    }


# ============================================================
# GAME FINISHED CHECK
# ============================================================

def is_game_finished(
    state: GameState,
) -> bool:

    result = check_victory(
        state
    )

    return result.finished


# ============================================================
# WINNER SIDE NAME
# ============================================================

def get_winner_name(
    winner: Optional[str],
) -> str:

    names = {
        STATUS_TAXT: "👑 Taxt",
        STATUS_QORA: "🩸 Qora",
        STATUS_ISYON: "🏴 Isyon",
        STATUS_MUSTAQIL: "☠️ Mustaqil",
    }

    return names.get(
        winner,
        "Noma'lum",
    )


# ============================================================
# GAME RESULT DATA
# ============================================================

def build_game_result(
    state: GameState,
) -> Dict:

    result = check_victory(
        state
    )

    return {
        "finished": result.finished,
        "winner": result.winner,
        "winner_name": get_winner_name(
            result.winner
        ),
        "winners": list(
            result.winners
        ),
        "reason": result.reason,
        "alive_by_side": dict(
            result.alive_by_side
        ),
  }
