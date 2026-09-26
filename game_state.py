# ============================================================
# THRONE — GAME STATE
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


# ============================================================
# GAME PHASES
# ============================================================

PHASE_LOBBY = "lobby"
PHASE_ROLE_REVEAL = "role_reveal"
PHASE_NIGHT = "night"
PHASE_DAY = "day"
PHASE_DISCUSSION = "discussion"
PHASE_VOTING = "voting"
PHASE_LAST_WORDS = "last_words"
PHASE_FINISHED = "finished"
PHASE_STOPPED = "stopped"


# ============================================================
# NIGHT ACTION PRIORITY
# ============================================================

NIGHT_ORDER = (
    "observe",
    "protect",
    "block",
    "poison",
    "weaken",
    "attack",
    "special",
)


# ============================================================
# PLAYER STATE
# ============================================================

@dataclass
class PlayerState:
    user_id: int
    username: str = ""
    first_name: str = ""

    role_key: Optional[str] = None
    side: Optional[str] = None

    alive: bool = True
    connected: bool = True

    last_words_used: bool = False
    night_action_used: bool = False
    vote_used: bool = False

    protected: bool = False
    blocked: bool = False
    poisoned: bool = False
    weakened: bool = False

    poison_turns: int = 0
    weakness_turns: int = 0

    custom_data: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ACTION STATE
# ============================================================

@dataclass
class ActionState:
    user_id: int
    action_type: str

    target_id: Optional[int] = None

    value: Any = None

    priority: int = 0
    resolved: bool = False


# ============================================================
# VOTE STATE
# ============================================================

@dataclass
class VoteState:
    voter_id: int
    target_id: int

    round_number: int = 1


# ============================================================
# GAME STATE
# ============================================================

@dataclass
class GameState:
    game_id: int
    chat_id: int
    creator_id: int

    phase: str = PHASE_LOBBY

    round_number: int = 0
    night_number: int = 0
    day_number: int = 0

    players: Dict[int, PlayerState] = field(default_factory=dict)

    night_actions: List[ActionState] = field(default_factory=list)
    votes: List[VoteState] = field(default_factory=list)

    eliminated_players: Set[int] = field(default_factory=set)

    last_eliminated_id: Optional[int] = None
    pending_last_words_id: Optional[int] = None

    winner: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# CREATE GAME STATE
# ============================================================

def create_game_state(
    game_id: int,
    chat_id: int,
    creator_id: int,
) -> GameState:
    return GameState(
        game_id=game_id,
        chat_id=chat_id,
        creator_id=creator_id,
    )


# ============================================================
# PLAYER MANAGEMENT
# ============================================================

def add_player(
    state: GameState,
    user_id: int,
    username: str = "",
    first_name: str = "",
) -> PlayerState:

    if user_id in state.players:
        return state.players[user_id]

    player = PlayerState(
        user_id=user_id,
        username=username,
        first_name=first_name,
    )

    state.players[user_id] = player

    return player


def remove_player(
    state: GameState,
    user_id: int,
) -> bool:

    if user_id not in state.players:
        return False

    del state.players[user_id]

    return True


def get_player(
    state: GameState,
    user_id: int,
) -> Optional[PlayerState]:

    return state.players.get(user_id)


def player_exists(
    state: GameState,
    user_id: int,
) -> bool:

    return user_id in state.players


# ============================================================
# PLAYER STATUS
# ============================================================

def is_alive(
    state: GameState,
    user_id: int,
) -> bool:

    player = get_player(state, user_id)

    if not player:
        return False

    return player.alive


def eliminate_player(
    state: GameState,
    user_id: int,
) -> bool:

    player = get_player(state, user_id)

    if not player:
        return False

    if not player.alive:
        return False

    player.alive = False

    state.eliminated_players.add(user_id)

    state.last_eliminated_id = user_id
    state.pending_last_words_id = user_id

    return True


# ============================================================
# ALIVE / DEAD PLAYERS
# ============================================================

def get_alive_players(
    state: GameState,
) -> List[PlayerState]:

    return [
        player
        for player in state.players.values()
        if player.alive
    ]


def get_dead_players(
    state: GameState,
) -> List[PlayerState]:

    return [
        player
        for player in state.players.values()
        if not player.alive
    ]


def alive_count(
    state: GameState,
) -> int:

    return len(get_alive_players(state))


def dead_count(
    state: GameState,
) -> int:

    return len(get_dead_players(state))


# ============================================================
# ROLE MANAGEMENT
# ============================================================

def assign_role(
    state: GameState,
    user_id: int,
    role_key: str,
    side: str,
) -> bool:

    player = get_player(state, user_id)

    if not player:
        return False

    player.role_key = role_key
    player.side = side

    return True


def get_role(
    state: GameState,
    user_id: int,
) -> Optional[str]:

    player = get_player(state, user_id)

    if not player:
        return None

    return player.role_key


def get_side(
    state: GameState,
    user_id: int,
) -> Optional[str]:

    player = get_player(state, user_id)

    if not player:
        return None

    return player.side


def get_players_by_side(
    state: GameState,
    side: str,
    alive_only: bool = True,
) -> List[PlayerState]:

    result = []

    for player in state.players.values():

        if player.side != side:
            continue

        if alive_only and not player.alive:
            continue

        result.append(player)

    return result


# ============================================================
# PHASE MANAGEMENT
# ============================================================

def set_phase(
    state: GameState,
    phase: str,
) -> None:

    state.phase = phase

    if phase == PHASE_NIGHT:
        state.night_number += 1
        state.round_number += 1

        reset_night_state(state)

    elif phase == PHASE_DAY:
        state.day_number += 1

    elif phase == PHASE_VOTING:
        reset_vote_state(state)


def get_phase(
    state: GameState,
) -> str:

    return state.phase


def is_phase(
    state: GameState,
    phase: str,
) -> bool:

    return state.phase == phase


# ============================================================
# NIGHT STATE
# ============================================================

def reset_night_state(
    state: GameState,
) -> None:

    state.night_actions.clear()

    for player in state.players.values():

        player.night_action_used = False
        player.protected = False
        player.blocked = False


def add_night_action(
    state: GameState,
    user_id: int,
    action_type: str,
    target_id: Optional[int] = None,
    value: Any = None,
) -> bool:

    player = get_player(state, user_id)

    if not player:
        return False

    if not player.alive:
        return False

    if player.night_action_used:
        return False

    if action_type not in NIGHT_ORDER:
        return False

    priority = NIGHT_ORDER.index(action_type)

    action = ActionState(
        user_id=user_id,
        action_type=action_type,
        target_id=target_id,
        value=value,
        priority=priority,
    )

    state.night_actions.append(action)

    player.night_action_used = True

    return True


def get_night_actions(
    state: GameState,
) -> List[ActionState]:

    return sorted(
        state.night_actions,
        key=lambda action: action.priority,
    )


def clear_night_actions(
    state: GameState,
) -> None:

    state.night_actions.clear()


# ============================================================
# EFFECTS
# ============================================================

def protect_player(
    state: GameState,
    user_id: int,
) -> bool:

    player = get_player(state, user_id)

    if not player or not player.alive:
        return False

    player.protected = True

    return True


def block_player(
    state: GameState,
    user_id: int,
) -> bool:

    player = get_player(state, user_id)

    if not player or not player.alive:
        return False

    player.blocked = True

    return True


def poison_player(
    state: GameState,
    user_id: int,
    turns: int = 1,
) -> bool:

    player = get_player(state, user_id)

    if not player or not player.alive:
        return False

    player.poisoned = True
    player.poison_turns = max(
        player.poison_turns,
        turns,
    )

    return True


def weaken_player(
    state: GameState,
    user_id: int,
    turns: int = 1,
) -> bool:

    player = get_player(state, user_id)

    if not player or not player.alive:
        return False

    player.weakened = True
    player.weakness_turns = max(
        player.weakness_turns,
        turns,
    )

    return True


def clear_temporary_effects(
    state: GameState,
) -> None:

    for player in state.players.values():

        player.protected = False
        player.blocked = False

        if player.poison_turns > 0:
            player.poison_turns -= 1

            if player.poison_turns <= 0:
                player.poisoned = False

        if player.weakness_turns > 0:
            player.weakness_turns -= 1

            if player.weakness_turns <= 0:
                player.weakened = False


# ============================================================
# VOTING
# ============================================================

def reset_vote_state(
    state: GameState,
) -> None:

    state.votes.clear()

    for player in state.players.values():
        player.vote_used = False


def add_vote(
    state: GameState,
    voter_id: int,
    target_id: int,
) -> bool:

    voter = get_player(state, voter_id)
    target = get_player(state, target_id)

    if not voter or not target:
        return False

    if not voter.alive:
        return False

    if not target.alive:
        return False

    if voter_id == target_id:
        return False

    if voter.vote_used:
        return False

    vote = VoteState(
        voter_id=voter_id,
        target_id=target_id,
    )

    state.votes.append(vote)

    voter.vote_used = True

    return True


def get_vote_counts(
    state: GameState,
) -> Dict[int, int]:

    counts: Dict[int, int] = {}

    for vote in state.votes:

        counts[vote.target_id] = (
            counts.get(vote.target_id, 0) + 1
        )

    return counts


def get_vote_result(
    state: GameState,
) -> Dict[str, Any]:

    counts = get_vote_counts(state)

    if not counts:
        return {
            "winner": None,
            "tie": False,
            "counts": {},
        }

    highest = max(counts.values())

    leaders = [
        user_id
        for user_id, count in counts.items()
        if count == highest
    ]

    if len(leaders) > 1:
        return {
            "winner": None,
            "tie": True,
            "leaders": leaders,
            "counts": counts,
        }

    return {
        "winner": leaders[0],
        "tie": False,
        "leaders": leaders,
        "counts": counts,
    }


# ============================================================
# LAST WORDS
# ============================================================

def can_use_last_words(
    state: GameState,
    user_id: int,
) -> bool:

    player = get_player(state, user_id)

    if not player:
        return False

    if player.last_words_used:
        return False

    return True


def use_last_words(
    state: GameState,
    user_id: int,
) -> bool:

    player = get_player(state, user_id)

    if not player:
        return False

    if player.last_words_used:
        return False

    player.last_words_used = True

    if state.pending_last_words_id == user_id:
        state.pending_last_words_id = None

    return True


# ============================================================
# VICTORY SUPPORT
# ============================================================

def count_sides(
    state: GameState,
) -> Dict[str, int]:

    result: Dict[str, int] = {}

    for player in get_alive_players(state):

        if not player.side:
            continue

        result[player.side] = (
            result.get(player.side, 0) + 1
        )

    return result


def get_alive_count_by_side(
    state: GameState,
    side: str,
) -> int:

    return len(
        get_players_by_side(
            state,
            side,
            alive_only=True,
        )
    )


# ============================================================
# GAME FINISH
# ============================================================

def finish_game(
    state: GameState,
    winner: str,
) -> None:

    state.winner = winner
    state.phase = PHASE_FINISHED


def stop_game(
    state: GameState,
) -> None:

    state.phase = PHASE_STOPPED


def is_finished(
    state: GameState,
) -> bool:

    return state.phase == PHASE_FINISHED


# ============================================================
# SERIALIZATION
# ============================================================

def player_to_dict(
    player: PlayerState,
) -> Dict[str, Any]:

    return {
        "user_id": player.user_id,
        "username": player.username,
        "first_name": player.first_name,
        "role_key": player.role_key,
        "side": player.side,
        "alive": player.alive,
        "connected": player.connected,
        "last_words_used": player.last_words_used,
        "night_action_used": player.night_action_used,
        "vote_used": player.vote_used,
        "protected": player.protected,
        "blocked": player.blocked,
        "poisoned": player.poisoned,
        "weakened": player.weakened,
        "poison_turns": player.poison_turns,
        "weakness_turns": player.weakness_turns,
        "custom_data": player.custom_data,
    }


def game_state_to_dict(
    state: GameState,
) -> Dict[str, Any]:

    return {
        "game_id": state.game_id,
        "chat_id": state.chat_id,
        "creator_id": state.creator_id,
        "phase": state.phase,
        "round_number": state.round_number,
        "night_number": state.night_number,
        "day_number": state.day_number,

        "players": {
            str(user_id): player_to_dict(player)
            for user_id, player in state.players.items()
        },

        "eliminated_players": list(
            state.eliminated_players
        ),

        "last_eliminated_id": state.last_eliminated_id,
        "pending_last_words_id": state.pending_last_words_id,
        "winner": state.winner,
        "metadata": state.metadata,
    }


# ============================================================
# SUMMARY
# ============================================================

def get_state_summary(
    state: GameState,
) -> Dict[str, Any]:

    return {
        "game_id": state.game_id,
        "chat_id": state.chat_id,
        "phase": state.phase,
        "round": state.round_number,
        "night": state.night_number,
        "day": state.day_number,
        "total_players": len(state.players),
        "alive_players": alive_count(state),
        "dead_players": dead_count(state),
        "winner": state.winner,
}
