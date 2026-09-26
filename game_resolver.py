# ============================================================
# THRONE — GAME RESOLVER
# ============================================================

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from game_state import (
    GameState,
    ActionState,
    get_player,
    is_alive,
    get_alive_players,
    eliminate_player,
)

from game_actions import (
    ACTION_OBSERVE,
    ACTION_PROTECT,
    ACTION_BLOCK,
    ACTION_POISON,
    ACTION_WEAKEN,
    ACTION_ATTACK,
    ACTION_SPECIAL,
    resolve_action,
)


# ============================================================
# RESOLUTION PRIORITY
# ============================================================

ACTION_PRIORITY = {
    ACTION_OBSERVE: 10,
    ACTION_PROTECT: 20,
    ACTION_BLOCK: 30,
    ACTION_POISON: 40,
    ACTION_WEAKEN: 50,
    ACTION_ATTACK: 60,
    ACTION_SPECIAL: 70,
}


# ============================================================
# RESOLUTION RESULT
# ============================================================

@dataclass
class ResolutionResult:
    success: bool
    message: str = ""
    eliminated: List[int] = None
    blocked: List[int] = None
    protected: List[int] = None
    poisoned: List[int] = None
    weakened: List[int] = None
    observations: Dict[int, Dict[str, Any]] = None

    def __post_init__(self):
        if self.eliminated is None:
            self.eliminated = []

        if self.blocked is None:
            self.blocked = []

        if self.protected is None:
            self.protected = []

        if self.poisoned is None:
            self.poisoned = []

        if self.weakened is None:
            self.weakened = []

        if self.observations is None:
            self.observations = {}


# ============================================================
# ACTION SORTING
# ============================================================

def get_action_priority(action: ActionState) -> int:
    return ACTION_PRIORITY.get(
        action.action_type,
        999,
    )


def sort_actions(
    actions: List[ActionState],
) -> List[ActionState]:

    return sorted(
        actions,
        key=get_action_priority,
    )


# ============================================================
# VALID ACTION CHECK
# ============================================================

def is_action_actor_alive(
    state: GameState,
    action: ActionState,
) -> bool:

    player = get_player(
        state,
        action.user_id,
    )

    return bool(
        player and player.alive
    )


# ============================================================
# COLLECT EFFECTS
# ============================================================

def collect_effects(
    results,
) -> Dict[str, Any]:

    effects = {
        "eliminated": [],
        "blocked": [],
        "protected": [],
        "poisoned": [],
        "weakened": [],
        "observations": {},
    }

    for result in results:

        if not result.success:
            continue

        if result.target_id is not None:

            if result.data.get("eliminated"):
                effects["eliminated"].append(
                    result.target_id
                )

            if result.data.get("blocked"):
                effects["blocked"].append(
                    result.target_id
                )

            if result.data.get("blocked_by_protection"):
                effects["protected"].append(
                    result.target_id
                )

        if result.action_type == ACTION_POISON:
            if result.target_id is not None:
                effects["poisoned"].append(
                    result.target_id
                )

        if result.action_type == ACTION_WEAKEN:
            if result.target_id is not None:
                effects["weakened"].append(
                    result.target_id
                )

        if result.action_type == ACTION_OBSERVE:
            if result.target_id is not None:
                effects["observations"][
                    result.user_id
                ] = {
                    "target_id": result.target_id,
                    "role_key": result.data.get(
                        "role_key"
                    ),
                    "side": result.data.get(
                        "side"
                    ),
                }

    return effects


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def unique_ids(
    values: List[int],
) -> List[int]:

    result = []
    seen = set()

    for value in values:

        if value in seen:
            continue

        seen.add(value)
        result.append(value)

    return result


# ============================================================
# PROTECTION CHECK
# ============================================================

def is_protected(
    protected_ids: List[int],
    user_id: int,
) -> bool:

    return user_id in protected_ids


# ============================================================
# ATTACK RESOLUTION
# ============================================================

def resolve_attacks(
    state: GameState,
    attack_actions: List[ActionState],
    protected_ids: List[int],
    blocked_ids: List[int],
) -> List[int]:

    eliminated = []

    for action in attack_actions:

        if not is_action_actor_alive(
            state,
            action,
        ):
            continue

        if action.user_id in blocked_ids:
            continue

        if action.target_id is None:
            continue

        target = get_player(
            state,
            action.target_id,
        )

        if not target or not target.alive:
            continue

        if is_protected(
            protected_ids,
            action.target_id,
        ):
            continue

        eliminate_player(
            state,
            action.target_id,
        )

        eliminated.append(
            action.target_id
        )

    return unique_ids(eliminated)


# ============================================================
# OBSERVATION RESOLUTION
# ============================================================

def resolve_observations(
    state: GameState,
    actions: List[ActionState],
) -> Dict[int, Dict[str, Any]]:

    observations = {}

    for action in actions:

        if not is_action_actor_alive(
            state,
            action,
        ):
            continue

        if action.target_id is None:
            continue

        target = get_player(
            state,
            action.target_id,
        )

        if not target:
            continue

        observations[action.user_id] = {
            "target_id": action.target_id,
            "role_key": target.role_key,
            "side": target.side,
        }

    return observations


# ============================================================
# FULL NIGHT RESOLUTION
# ============================================================

def resolve_night(
    state: GameState,
) -> ResolutionResult:

    actions = list(
        getattr(
            state,
            "night_actions",
            [],
        )
    )

    if not actions:
        return ResolutionResult(
            success=True,
            message="🌙 Bu tun hech qanday harakat amalga oshirilmadi.",
        )

    actions = sort_actions(
        actions
    )

    # --------------------------------------------------------
    # Separate action types
    # --------------------------------------------------------

    observe_actions = [
        a for a in actions
        if a.action_type == ACTION_OBSERVE
    ]

    protect_actions = [
        a for a in actions
        if a.action_type == ACTION_PROTECT
    ]

    block_actions = [
        a for a in actions
        if a.action_type == ACTION_BLOCK
    ]

    poison_actions = [
        a for a in actions
        if a.action_type == ACTION_POISON
    ]

    weaken_actions = [
        a for a in actions
        if a.action_type == ACTION_WEAKEN
    ]

    attack_actions = [
        a for a in actions
        if a.action_type == ACTION_ATTACK
    ]

    special_actions = [
        a for a in actions
        if a.action_type == ACTION_SPECIAL
    ]

    # --------------------------------------------------------
    # BLOCKED PLAYERS
    # --------------------------------------------------------

    blocked_ids = []

    for action in block_actions:

        if not is_action_actor_alive(
            state,
            action,
        ):
            continue

        if action.target_id is None:
            continue

        target = get_player(
            state,
            action.target_id,
        )

        if not target or not target.alive:
            continue

        blocked_ids.append(
            action.target_id
        )

    blocked_ids = unique_ids(
        blocked_ids
    )

    # --------------------------------------------------------
    # PROTECTED PLAYERS
    # --------------------------------------------------------

    protected_ids = []

    for action in protect_actions:

        if not is_action_actor_alive(
            state,
            action,
        ):
            continue

        if action.user_id in blocked_ids:
            continue

        if action.target_id is None:
            continue

        target = get_player(
            state,
            action.target_id,
        )

        if not target or not target.alive:
            continue

        protected_ids.append(
            action.target_id
        )

    protected_ids = unique_ids(
        protected_ids
    )

    # --------------------------------------------------------
    # OBSERVATIONS
    # --------------------------------------------------------

    observations = resolve_observations(
        state,
        observe_actions,
    )

    # --------------------------------------------------------
    # POISON
    # --------------------------------------------------------

    poisoned_ids = []

    for action in poison_actions:

        if not is_action_actor_alive(
            state,
            action,
        ):
            continue

        if action.user_id in blocked_ids:
            continue

        if action.target_id is None:
            continue

        target = get_player(
            state,
            action.target_id,
        )

        if not target or not target.alive:
            continue

        poisoned_ids.append(
            action.target_id
        )

    poisoned_ids = unique_ids(
        poisoned_ids
    )

    # --------------------------------------------------------
    # WEAKEN
    # --------------------------------------------------------

    weakened_ids = []

    for action in weaken_actions:

        if not is_action_actor_alive(
            state,
            action,
        ):
            continue

        if action.user_id in blocked_ids:
            continue

        if action.target_id is None:
            continue

        target = get_player(
            state,
            action.target_id,
        )

        if not target or not target.alive:
            continue

        weakened_ids.append(
            action.target_id
        )

    weakened_ids = unique_ids(
        weakened_ids
    )

    # --------------------------------------------------------
    # ATTACK
    # --------------------------------------------------------

    eliminated_ids = resolve_attacks(
        state,
        attack_actions,
        protected_ids,
        blocked_ids,
    )

    # --------------------------------------------------------
    # SPECIAL ACTIONS
    # --------------------------------------------------------

    for action in special_actions:

        if not is_action_actor_alive(
            state,
            action,
        ):
            continue

        if action.user_id in blocked_ids:
            continue

        # Maxsus qobiliyatlar keyinchalik
        # role-specific engine orqali ishlaydi.
        pass

    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return ResolutionResult(
        success=True,
        message="🌅 Tun yakunlandi.",
        eliminated=eliminated_ids,
        blocked=blocked_ids,
        protected=protected_ids,
        poisoned=poisoned_ids,
        weakened=weakened_ids,
        observations=observations,
    )


# ============================================================
# MORNING REPORT
# ============================================================

def build_morning_report(
    result: ResolutionResult,
) -> Dict[str, Any]:

    report = {
        "death_count": len(
            result.eliminated
        ),
        "deaths": result.eliminated,
        "protected_count": len(
            result.protected
        ),
        "poisoned_count": len(
            result.poisoned
        ),
        "weakened_count": len(
            result.weakened
        ),
        "blocked_count": len(
            result.blocked
        ),
    }

    return report


# ============================================================
# PUBLIC MORNING MESSAGE
# ============================================================

def get_morning_message(
    result: ResolutionResult,
) -> str:

    if not result.eliminated:

        if result.protected:
            return (
                "🌅 Tong otdi.\n\n"
                "🏰 Qirollik omon qoldi.\n"
                "🛡️ Kecha qilingan hujumlar to'xtatildi."
            )

        return (
            "🌅 Tong otdi.\n\n"
            "🏰 Bu tun hech kim o'ldirilmadi."
        )

    if len(result.eliminated) == 1:

        return (
            "🌅 Tong otdi.\n\n"
            "⚔️ Kecha qirollikda hujum sodir bo'ldi.\n"
            "☠️ Bir o'yinchi o'yinni tark etdi."
        )

    return (
        "🌅 Tong otdi.\n\n"
        "⚔️ Kecha qirollikda bir nechta hujum sodir bo'ldi.\n"
        "☠️ Bir nechta o'yinchi o'yinni tark etdi."
    )


# ============================================================
# GAME VICTORY SUPPORT
# ============================================================

def get_alive_sides(
    state: GameState,
) -> Dict[str, int]:

    sides: Dict[str, int] = {}

    for player in get_alive_players(state):

        side = player.side or "Noma'lum"

        sides[side] = (
            sides.get(side, 0) + 1
        )

    return sides


def has_alive_side(
    state: GameState,
    side: str,
) -> bool:

    for player in get_alive_players(state):

        if player.side == side:
            return True

    return False


# ============================================================
# RESOLUTION SUMMARY
# ============================================================

def get_resolution_summary(
    result: ResolutionResult,
) -> Dict[str, Any]:

    return {
        "success": result.success,
        "eliminated": list(
            result.eliminated
        ),
        "blocked": list(
            result.blocked
        ),
        "protected": list(
            result.protected
        ),
        "poisoned": list(
            result.poisoned
        ),
        "weakened": list(
            result.weakened
        ),
        "observations": dict(
            result.observations
        ),
}
