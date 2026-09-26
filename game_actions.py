# ============================================================
# THRONE — GAME ACTIONS
# ============================================================

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from game_state import (
    GameState,
    ActionState,
    get_player,
    is_alive,
    add_night_action,
    get_night_actions,
    protect_player,
    block_player,
    poison_player,
    weaken_player,
    eliminate_player,
)


# ============================================================
# ACTION TYPES
# ============================================================

ACTION_OBSERVE = "observe"
ACTION_PROTECT = "protect"
ACTION_BLOCK = "block"
ACTION_POISON = "poison"
ACTION_WEAKEN = "weaken"
ACTION_ATTACK = "attack"
ACTION_SPECIAL = "special"


VALID_ACTIONS = {
    ACTION_OBSERVE,
    ACTION_PROTECT,
    ACTION_BLOCK,
    ACTION_POISON,
    ACTION_WEAKEN,
    ACTION_ATTACK,
    ACTION_SPECIAL,
}


# ============================================================
# RESULT
# ============================================================

@dataclass
class ActionResult:
    success: bool
    action_type: str
    user_id: int
    target_id: Optional[int] = None
    message: str = ""
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


# ============================================================
# ACTION VALIDATION
# ============================================================

def validate_action(
    state: GameState,
    user_id: int,
    action_type: str,
    target_id: Optional[int] = None,
) -> ActionResult:

    player = get_player(state, user_id)

    if not player:
        return ActionResult(
            False,
            action_type,
            user_id,
            target_id,
            "O'yinchi topilmadi.",
        )

    if not player.alive:
        return ActionResult(
            False,
            action_type,
            user_id,
            target_id,
            "Eliminatsiya qilingan o'yinchi harakat qila olmaydi.",
        )

    if action_type not in VALID_ACTIONS:
        return ActionResult(
            False,
            action_type,
            user_id,
            target_id,
            "Noma'lum harakat turi.",
        )

    if action_type != ACTION_SPECIAL and target_id is None:
        return ActionResult(
            False,
            action_type,
            user_id,
            target_id,
            "Nishon tanlanmagan.",
        )

    if target_id is not None:

        target = get_player(state, target_id)

        if not target:
            return ActionResult(
                False,
                action_type,
                user_id,
                target_id,
                "Nishon topilmadi.",
            )

        if not target.alive:
            return ActionResult(
                False,
                action_type,
                user_id,
                target_id,
                "Tanlangan nishon allaqachon o'yindan chiqqan.",
            )

    if action_type == ACTION_ATTACK and target_id == user_id:
        return ActionResult(
            False,
            action_type,
            user_id,
            target_id,
            "O'zingizga hujum qila olmaysiz.",
        )

    return ActionResult(
        True,
        action_type,
        user_id,
        target_id,
        "Harakat qabul qilindi.",
    )


# ============================================================
# SUBMIT ACTION
# ============================================================

def submit_action(
    state: GameState,
    user_id: int,
    action_type: str,
    target_id: Optional[int] = None,
    value: Any = None,
) -> ActionResult:

    validation = validate_action(
        state,
        user_id,
        action_type,
        target_id,
    )

    if not validation.success:
        return validation

    success = add_night_action(
        state,
        user_id,
        action_type,
        target_id,
        value,
    )

    if not success:
        return ActionResult(
            False,
            action_type,
            user_id,
            target_id,
            "Bu harakatni hozir amalga oshirib bo'lmaydi.",
        )

    return ActionResult(
        True,
        action_type,
        user_id,
        target_id,
        "🌙 Tungi harakatingiz qabul qilindi.",
        {
            "value": value,
        },
    )


# ============================================================
# OBSERVE
# ============================================================

def resolve_observe(
    state: GameState,
    action: ActionState,
) -> ActionResult:

    target = get_player(
        state,
        action.target_id,
    )

    if not target:
        return ActionResult(
            False,
            ACTION_OBSERVE,
            action.user_id,
            action.target_id,
            "Nishon topilmadi.",
        )

    return ActionResult(
        True,
        ACTION_OBSERVE,
        action.user_id,
        action.target_id,
        "Kuzatuv yakunlandi.",
        {
            "role_key": target.role_key,
            "side": target.side,
        },
    )


# ============================================================
# PROTECT
# ============================================================

def resolve_protect(
    state: GameState,
    action: ActionState,
) -> ActionResult:

    success = protect_player(
        state,
        action.target_id,
    )

    if not success:
        return ActionResult(
            False,
            ACTION_PROTECT,
            action.user_id,
            action.target_id,
            "Himoya amalga oshmadi.",
        )

    return ActionResult(
        True,
        ACTION_PROTECT,
        action.user_id,
        action.target_id,
        "🛡️ Himoya amalga oshirildi.",
    )


# ============================================================
# BLOCK
# ============================================================

def resolve_block(
    state: GameState,
    action: ActionState,
) -> ActionResult:

    success = block_player(
        state,
        action.target_id,
    )

    if not success:
        return ActionResult(
            False,
            ACTION_BLOCK,
            action.user_id,
            action.target_id,
            "Harakatni bloklash amalga oshmadi.",
        )

    return ActionResult(
        True,
        ACTION_BLOCK,
        action.user_id,
        action.target_id,
        "⛓️ Harakat bloklandi.",
    )


# ============================================================
# POISON
# ============================================================

def resolve_poison(
    state: GameState,
    action: ActionState,
) -> ActionResult:

    turns = 1

    if isinstance(action.value, int):
        turns = max(1, min(action.value, 5))

    success = poison_player(
        state,
        action.target_id,
        turns,
    )

    if not success:
        return ActionResult(
            False,
            ACTION_POISON,
            action.user_id,
            action.target_id,
            "Zahar ta'siri berilmadi.",
        )

    return ActionResult(
        True,
        ACTION_POISON,
        action.user_id,
        action.target_id,
        "☠️ Zahar ta'siri qo'llandi.",
        {
            "turns": turns,
        },
    )


# ============================================================
# WEAKEN
# ============================================================

def resolve_weaken(
    state: GameState,
    action: ActionState,
) -> ActionResult:

    turns = 1

    if isinstance(action.value, int):
        turns = max(1, min(action.value, 5))

    success = weaken_player(
        state,
        action.target_id,
        turns,
    )

    if not success:
        return ActionResult(
            False,
            ACTION_WEAKEN,
            action.user_id,
            action.target_id,
            "Zaiflashtirish amalga oshmadi.",
        )

    return ActionResult(
        True,
        ACTION_WEAKEN,
        action.user_id,
        action.target_id,
        "🩸 Nishon zaiflashtirildi.",
        {
            "turns": turns,
        },
    )


# ============================================================
# ATTACK
# ============================================================

def resolve_attack(
    state: GameState,
    action: ActionState,
) -> ActionResult:

    attacker = get_player(
        state,
        action.user_id,
    )

    target = get_player(
        state,
        action.target_id,
    )

    if not attacker or not target:
        return ActionResult(
            False,
            ACTION_ATTACK,
            action.user_id,
            action.target_id,
            "Hujum uchun o'yinchi topilmadi.",
        )

    if not attacker.alive:
        return ActionResult(
            False,
            ACTION_ATTACK,
            action.user_id,
            action.target_id,
            "Hujumchi tirik emas.",
        )

    if not target.alive:
        return ActionResult(
            False,
            ACTION_ATTACK,
            action.user_id,
            action.target_id,
            "Nishon tirik emas.",
        )

    # Himoyalangan nishon hujumdan omon qoladi.
    if target.protected:
        return ActionResult(
            True,
            ACTION_ATTACK,
            action.user_id,
            action.target_id,
            "🛡️ Hujum himoya tufayli to'xtatildi.",
            {
                "blocked_by_protection": True,
            },
        )

    # Bloklangan hujumchi hujum qila olmaydi.
    if attacker.blocked:
        return ActionResult(
            True,
            ACTION_ATTACK,
            action.user_id,
            action.target_id,
            "⛓️ Hujum bloklandi.",
            {
                "blocked": True,
            },
        )

    eliminate_player(
        state,
        action.target_id,
    )

    return ActionResult(
        True,
        ACTION_ATTACK,
        action.user_id,
        action.target_id,
        "⚔️ Hujum muvaffaqiyatli amalga oshirildi.",
        {
            "eliminated": True,
        },
    )


# ============================================================
# SPECIAL
# ============================================================

def resolve_special(
    state: GameState,
    action: ActionState,
) -> ActionResult:

    return ActionResult(
        True,
        ACTION_SPECIAL,
        action.user_id,
        action.target_id,
        "✨ Maxsus qobiliyat qayta ishlash uchun yuborildi.",
        {
            "value": action.value,
        },
    )


# ============================================================
# SINGLE ACTION RESOLUTION
# ============================================================

def resolve_action(
    state: GameState,
    action: ActionState,
) -> ActionResult:

    if action.resolved:
        return ActionResult(
            False,
            action.action_type,
            action.user_id,
            action.target_id,
            "Bu harakat allaqachon bajarilgan.",
        )

    if action.action_type == ACTION_OBSERVE:
        result = resolve_observe(state, action)

    elif action.action_type == ACTION_PROTECT:
        result = resolve_protect(state, action)

    elif action.action_type == ACTION_BLOCK:
        result = resolve_block(state, action)

    elif action.action_type == ACTION_POISON:
        result = resolve_poison(state, action)

    elif action.action_type == ACTION_WEAKEN:
        result = resolve_weaken(state, action)

    elif action.action_type == ACTION_ATTACK:
        result = resolve_attack(state, action)

    elif action.action_type == ACTION_SPECIAL:
        result = resolve_special(state, action)

    else:
        result = ActionResult(
            False,
            action.action_type,
            action.user_id,
            action.target_id,
            "Noma'lum harakat.",
        )

    action.resolved = True

    return result


# ============================================================
# RESOLVE ALL NIGHT ACTIONS
# ============================================================

def resolve_all_night_actions(
    state: GameState,
) -> List[ActionResult]:

    results: List[ActionResult] = []

    actions = get_night_actions(state)

    for action in actions:

        # Agar harakat qiluvchi tun davomida
        # o'yindan chiqarilgan bo'lsa, uning harakati
        # bajarilmaydi.
        actor = get_player(
            state,
            action.user_id,
        )

        if not actor or not actor.alive:
            action.resolved = True

            results.append(
                ActionResult(
                    False,
                    action.action_type,
                    action.user_id,
                    action.target_id,
                    "Harakat bajarilmadi: o'yinchi tirik emas.",
                )
            )

            continue

        result = resolve_action(
            state,
            action,
        )

        results.append(result)

    return results


# ============================================================
# ACTION STATISTICS
# ============================================================

def count_actions(
    state: GameState,
) -> Dict[str, int]:

    result: Dict[str, int] = {}

    for action in state.night_actions:

        action_type = action.action_type

        result[action_type] = (
            result.get(action_type, 0) + 1
        )

    return result


def get_player_actions(
    state: GameState,
    user_id: int,
) -> List[ActionState]:

    return [
        action
        for action in state.night_actions
        if action.user_id == user_id
    ]


def get_target_actions(
    state: GameState,
    target_id: int,
) -> List[ActionState]:

    return [
        action
        for action in state.night_actions
        if action.target_id == target_id
    ]


# ============================================================
# PUBLIC ATMOSPHERE MESSAGES
# ============================================================

def get_action_atmosphere(
    action_type: str,
) -> str:

    messages = {
        ACTION_OBSERVE:
            "🕵️ Qirollik tun zulmatida kimnidir kuzatmoqda.",

        ACTION_PROTECT:
            "🛡️ Saroy qo'riqchilari tun davomida bir hududni himoya qilmoqda.",

        ACTION_BLOCK:
            "⛓️ Tun qorong'usida kimningdir yo'li to'sildi.",

        ACTION_POISON:
            "☠️ Saroyda yashirin zahar izlari paydo bo'ldi.",

        ACTION_WEAKEN:
            "🩸 Kimdir tun davomida kuchini yo'qotdi.",

        ACTION_ATTACK:
            "⚔️ Tun sukunatini yashirin jang ovozi buzdi.",

        ACTION_SPECIAL:
            "✨ Qirollikda noma'lum kuch harakatga keldi.",
    }

    return messages.get(
        action_type,
        "🌙 Tun davomida noma'lum voqea yuz berdi.",
    )


# ============================================================
# ACTION RESULT SUMMARY
# ============================================================

def build_night_summary(
    results: List[ActionResult],
) -> Dict[str, Any]:

    summary = {
        "total": len(results),
        "successful": 0,
        "failed": 0,
        "eliminated": [],
        "blocked": [],
        "protected": [],
        "poisoned": [],
        "weakened": [],
    }

    for result in results:

        if result.success:
            summary["successful"] += 1
        else:
            summary["failed"] += 1

        if result.data.get("eliminated"):
            if result.target_id is not None:
                summary["eliminated"].append(
                    result.target_id
                )

        if result.data.get("blocked"):
            if result.target_id is not None:
                summary["blocked"].append(
                    result.target_id
                )

        if result.data.get("blocked_by_protection"):
            if result.target_id is not None:
                summary["protected"].append(
                    result.target_id
                )

        if result.action_type == ACTION_POISON:
            if result.target_id is not None:
                summary["poisoned"].append(
                    result.target_id
                )

        if result.action_type == ACTION_WEAKEN:
            if result.target_id is not None:
                summary["weakened"].append(
                    result.target_id
                )

    return summary
