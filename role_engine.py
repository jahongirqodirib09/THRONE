from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from roles import Role, Side, get_role


@dataclass
class RoleAction:
    """O'yinchining bitta tungi yoki kunduzgi harakati."""

    actor_id: int
    action_type: str
    target_id: Optional[int] = None

    value: int = 0
    success: bool = False
    blocked: bool = False
    reason: str = ""

    metadata: dict = field(default_factory=dict)


@dataclass
class RoleMemory:
    """Rolga tegishli vaqtinchalik xotira."""

    uses_left: dict[str, int] = field(default_factory=dict)
    cooldowns: dict[str, int] = field(default_factory=dict)

    last_target: dict[str, int] = field(default_factory=dict)

    blocked_players: set[int] = field(default_factory=set)
    protected_players: set[int] = field(default_factory=set)

    fake_checks: set[int] = field(default_factory=set)
    hidden_checks: set[int] = field(default_factory=set)

    visited: dict[int, list[int]] = field(default_factory=dict)


class RoleEngine:
    """
    THRONE rollarining asosiy mexanik dvigateli.

    Bu klass:
    - rolni tekshiradi
    - targetni tekshiradi
    - cooldownni nazorat qiladi
    - foydalanish sonini nazorat qiladi
    - bloklash/himoya/tekshiruv/hujumlarni tayyorlaydi

    Yakuniy o'lim va g'alaba qarorini game_resolver.py bajaradi.
    """

    def __init__(self):
        self.memories: dict[int, RoleMemory] = {}

    # =========================================================
    # XOTIRA
    # =========================================================

    def get_memory(self, user_id: int) -> RoleMemory:
        if user_id not in self.memories:
            self.memories[user_id] = RoleMemory()

        return self.memories[user_id]

    def clear_player_memory(self, user_id: int) -> None:
        self.memories.pop(user_id, None)

    def clear_game_memory(self) -> None:
        self.memories.clear()

    # =========================================================
    # ROLNI OLISH
    # =========================================================

    @staticmethod
    def get_player_role(role_key: Optional[str]) -> Optional[Role]:
        if not role_key:
            return None

        return get_role(role_key)

    # =========================================================
    # UMUMIY TEKSHIRUVLAR
    # =========================================================

    def can_use_role(
        self,
        user_id: int,
        role_key: str,
    ) -> tuple[bool, str]:
        role = get_role(role_key)

        if role is None:
            return False, "Noma'lum rol."

        memory = self.get_memory(user_id)

        # Foydalanish chegarasi
        if role.uses is not None:
            used = memory.uses_left.get(role_key, role.uses)

            if used <= 0:
                return False, "Bu qobiliyatdan foydalanish limiti tugagan."

        # Cooldown
        cooldown = memory.cooldowns.get(role_key, 0)

        if cooldown > 0:
            return False, f"Qobiliyat hali {cooldown} tun kutishni talab qiladi."

        return True, ""

    def consume_use(self, user_id: int, role_key: str) -> None:
        role = get_role(role_key)

        if role is None or role.uses is None:
            return

        memory = self.get_memory(user_id)

        current = memory.uses_left.get(
            role_key,
            role.uses,
        )

        memory.uses_left[role_key] = max(0, current - 1)

    def set_cooldown(
        self,
        user_id: int,
        role_key: str,
        cooldown: int,
    ) -> None:
        memory = self.get_memory(user_id)

        if cooldown > 0:
            memory.cooldowns[role_key] = cooldown
        else:
            memory.cooldowns.pop(role_key, None)

    def tick_cooldowns(self) -> None:
        """
        Har yangi tun boshlanganda cooldownlar kamayadi.
        """

        for memory in self.memories.values():
            expired = []

            for role_key, value in memory.cooldowns.items():
                new_value = max(0, value - 1)

                if new_value == 0:
                    expired.append(role_key)
                else:
                    memory.cooldowns[role_key] = new_value

            for role_key in expired:
                memory.cooldowns.pop(role_key, None)

    # =========================================================
    # TARGET TEKSHIRUVI
    # =========================================================

    @staticmethod
    def validate_target(
        actor_id: int,
        target_id: Optional[int],
        players: dict,
        *,
        allow_self: bool = False,
    ) -> tuple[bool, str]:

        if target_id is None:
            return False, "Nishon tanlanmagan."

        if target_id not in players:
            return False, "Nishon topilmadi."

        target = players[target_id]

        if not getattr(target, "joined", False):
            return False, "Bu o'yinchi o'yinda emas."

        if not getattr(target, "alive", False):
            return False, "Bu o'yinchi tirik emas."

        if not allow_self and actor_id == target_id:
            return False, "O'zingizni nishonga ola olmaysiz."

        return True, ""

    @staticmethod
    def same_target_last_night(
        user_id: int,
        target_id: int,
        memory: RoleMemory,
    ) -> bool:
        return memory.last_target.get(str(user_id)) == target_id

    # =========================================================
    # 🔒 BLOKLASH
    # =========================================================

    def block_action(
        self,
        actor_id: int,
        target_id: int,
        role_key: str,
        players: dict,
    ) -> RoleAction:

        valid, reason = self.validate_target(
            actor_id,
            target_id,
            players,
            allow_self=False,
        )

        if not valid:
            return RoleAction(
                actor_id=actor_id,
                action_type="block",
                target_id=target_id,
                reason=reason,
            )

        allowed, reason = self.can_use_role(
            actor_id,
            role_key,
        )

        if not allowed:
            return RoleAction(
                actor_id=actor_id,
                action_type="block",
                target_id=target_id,
                reason=reason,
            )

        memory = self.get_memory(actor_id)

        memory.blocked_players.add(target_id)
        memory.last_target[str(actor_id)] = target_id

        self.consume_use(actor_id, role_key)

        return RoleAction(
            actor_id=actor_id,
            action_type="block",
            target_id=target_id,
            success=True,
            reason="Nishonning tungi qobiliyati bloklandi.",
        )

    def is_blocked(self, target_id: int) -> bool:
        for memory in self.memories.values():
            if target_id in memory.blocked_players:
                return True

        return False

    # =========================================================
    # 🛡️ HIMOYA
    # =========================================================

    def protect(
        self,
        actor_id: int,
        target_id: int,
        role_key: str,
        players: dict,
    ) -> RoleAction:

        valid, reason = self.validate_target(
            actor_id,
            target_id,
            players,
            allow_self=False,
        )

        if not valid:
            return RoleAction(
                actor_id=actor_id,
                action_type="protect",
                target_id=target_id,
                reason=reason,
            )

        allowed, reason = self.can_use_role(
            actor_id,
            role_key,
        )

        if not allowed:
            return RoleAction(
                actor_id=actor_id,
                action_type="protect",
                target_id=target_id,
                reason=reason,
            )

        memory = self.get_memory(actor_id)

        previous_target = memory.last_target.get(str(actor_id))

        if previous_target == target_id:
            return RoleAction(
                actor_id=actor_id,
                action_type="protect",
                target_id=target_id,
                reason="Bir o'yinchini ketma-ket ikki tun himoya qilib bo'lmaydi.",
            )

        memory.protected_players.add(target_id)
        memory.last_target[str(actor_id)] = target_id

        # Cheksiz qobiliyat bo'lsa ham cooldown alohida boshqariladi.
        self.consume_use(actor_id, role_key)

        return RoleAction(
            actor_id=actor_id,
            action_type="protect",
            target_id=target_id,
            success=True,
            reason="Nishon himoyalandi.",
        )

    def is_protected(self, target_id: int) -> bool:
        for memory in self.memories.values():
            if target_id in memory.protected_players:
                return True

        return False

    # =========================================================
    # 🔎 TEKSHIRUV
    # =========================================================

    def investigate(
        self,
        actor_id: int,
        target_id: int,
        role_key: str,
        players: dict,
    ) -> RoleAction:

        valid, reason = self.validate_target(
            actor_id,
            target_id,
            players,
            allow_self=False,
        )

        if not valid:
            return RoleAction(
                actor_id=actor_id,
                action_type="investigate",
                target_id=target_id,
                reason=reason,
            )

        allowed, reason = self.can_use_role(
            actor_id,
            role_key,
        )

        if not allowed:
            return RoleAction(
                actor_id=actor_id,
                action_type="investigate",
                target_id=target_id,
                reason=reason,
            )

        target = players[target_id]
        target_role = get_role(getattr(target, "role", None))

        if target_role is None:
            result = "noma'lum"
        else:
            result = target_role.side.value

        # Soxta Maslahatchi uchun keyingi resolver
        # natijani o'zgartira olishi uchun metadata saqlanadi.
        action = RoleAction(
            actor_id=actor_id,
            action_type="investigate",
            target_id=target_id,
            success=True,
            metadata={
                "result": result,
                "target_role": getattr(target, "role", None),
            },
        )

        return action

    # =========================================================
    # 🎭 SOXTA MASLAHATCHI
    # =========================================================

    def activate_fake_check(
        self,
        actor_id: int,
        role_key: str,
        players: dict,
    ) -> RoleAction:

        if role_key != "soxta_maslahatchi":
            return RoleAction(
                actor_id=actor_id,
                action_type="fake_check",
                reason="Bu qobiliyat faqat Soxta maslahatchiga tegishli.",
            )

        allowed, reason = self.can_use_role(
            actor_id,
            role_key,
        )

        if not allowed:
            return RoleAction(
                actor_id=actor_id,
                action_type="fake_check",
                reason=reason,
            )

        memory = self.get_memory(actor_id)
        memory.fake_checks.add(actor_id)

        self.consume_use(actor_id, role_key)

        return RoleAction(
            actor_id=actor_id,
            action_type="fake_check",
            success=True,
            reason="Soxta tekshiruv qobiliyati faollashtirildi.",
        )

    def has_fake_check(self, user_id: int) -> bool:
        return user_id in self.get_memory(user_id).fake_checks

    # =========================================================
    # 🌑 SOYA BOSHLIG'I — QORA NIQOB
    # =========================================================

    def activate_shadow_mask(
        self,
        actor_id: int,
        role_key: str,
    ) -> RoleAction:

        if role_key != "soya_boshligi":
            return RoleAction(
                actor_id=actor_id,
                action_type="shadow_mask",
                reason="Bu qobiliyat Soya boshlig'iga tegishli.",
            )

        allowed, reason = self.can_use_role(
            actor_id,
            role_key,
        )

        if not allowed:
            return RoleAction(
                actor_id=actor_id,
                action_type="shadow_mask",
                reason=reason,
            )

        memory = self.get_memory(actor_id)
        memory.hidden_checks.add(actor_id)

        self.consume_use(actor_id, role_key)

        return RoleAction(
            actor_id=actor_id,
            action_type="shadow_mask",
            success=True,
            reason="Soya tomoni tekshiruvdan yashirildi.",
        )

    def has_shadow_mask(self, user_id: int) -> bool:
        return user_id in self.get_memory(user_id).hidden_checks

    # =========================================================
    # ⚔️ HUJUM
    # =========================================================

    def attack(
        self,
        actor_id: int,
        target_id: int,
        role_key: str,
        players: dict,
        *,
        attack_type: str = "ordinary",
        bypass_defense: bool = False,
    ) -> RoleAction:

        valid, reason = self.validate_target(
            actor_id,
            target_id,
            players,
            allow_self=False,
        )

        if not valid:
            return RoleAction(
                actor_id=actor_id,
                action_type="attack",
                target_id=target_id,
                reason=reason,
            )

        allowed, reason = self.can_use_role(
            actor_id,
            role_key,
        )

        if not allowed:
            return RoleAction(
                actor_id=actor_id,
                action_type="attack",
                target_id=target_id,
                reason=reason,
            )

        actor = players[actor_id]
        target = players[target_id]

        # Soya rollari o'z sherigiga oddiy hujum qila olmaydi.
        actor_role = get_role(getattr(actor, "role", None))
        target_role = get_role(getattr(target, "role", None))

        if (
            actor_role is not None
            and target_role is not None
            and actor_role.side == Side.SHADOW
            and target_role.side == Side.SHADOW
        ):
            return RoleAction(
                actor_id=actor_id,
                action_type="attack",
                target_id=target_id,
                reason="Soya o'yinchisi Soya sherigiga hujum qila olmaydi.",
            )

        memory = self.get_memory(actor_id)
        memory.last_target[str(actor_id)] = target_id

        self.consume_use(actor_id, role_key)

        return RoleAction(
            actor_id=actor_id,
            action_type="attack",
            target_id=target_id,
            success=True,
            metadata={
                "attack_type": attack_type,
                "bypass_defense": bypass_defense,
            },
            reason="Hujum tayyorlandi.",
        )

    # =========================================================
    # 👑 DUSHMAN QIROLI — ODDIY HIMOYANI CHEtlab o'tish
    # =========================================================

    def activate_attack_bypass(
        self,
        actor_id: int,
        role_key: str,
    ) -> RoleAction:

        if role_key != "dushman_qiroli":
            return RoleAction(
                actor_id=actor_id,
                action_type="attack_bypass",
                reason="Bu qobiliyat Dushman qiroliga tegishli.",
            )

        allowed, reason = self.can_use_role(
            actor_id,
            role_key,
        )

        if not allowed:
            return RoleAction(
                actor_id=actor_id,
                action_type="attack_bypass",
                reason=reason,
            )

        self.consume_use(actor_id, role_key)

        return RoleAction(
            actor_id=actor_id,
            action_type="attack_bypass",
            success=True,
            metadata={
                "bypass_ordinary_defense": True,
                "bypass_special_defense": False,
            },
            reason="Soya hujumi oddiy himoyani chetlab o'tish uchun kuchaytirildi.",
        )

    # =========================================================
    # 💰 QAROQI
    # =========================================================

    def steal_gold(
        self,
        actor_id: int,
        target_id: int,
        players: dict,
    ) -> RoleAction:

        valid, reason = self.validate_target(
            actor_id,
            target_id,
            players,
            allow_self=False,
        )

        if not valid:
            return RoleAction(
                actor_id=actor_id,
                action_type="steal_gold",
                target_id=target_id,
                reason=reason,
            )

        actor = players[actor_id]

        if getattr(actor, "role", None) != "qaroqi":
            return RoleAction(
                actor_id=actor_id,
                action_type="steal_gold",
                target_id=target_id,
                reason="Bu harakat faqat Qaroqiga tegishli.",
            )

        target = players[target_id]

        gold = int(getattr(target, "gold", 0))

        if gold >= 200:
            stolen = 200
        elif gold > 0:
            stolen = gold
        else:
            stolen = 0

        return RoleAction(
            actor_id=actor_id,
            action_type="steal_gold",
            target_id=target_id,
            value=stolen,
            success=stolen > 0,
            metadata={
                "requested": 200,
                "available": gold,
            },
            reason=(
                "200 Gold o'g'irlanadi."
                if stolen == 200
                else (
                    "Mavjud Goldning hammasi o'g'irlanadi."
                    if stolen > 0
                    else "Nishonda Gold yo'q."
                )
            ),
        )

    # =========================================================
    # 🩺 TABIB
    # =========================================================

    def heal(
        self,
        actor_id: int,
        target_id: int,
        role_key: str,
        players: dict,
    ) -> RoleAction:

        valid, reason = self.validate_target(
            actor_id,
            target_id,
            players,
            allow_self=False,
        )

        if not valid:
            return RoleAction(
                actor_id=actor_id,
                action_type="heal",
                target_id=target_id,
                reason=reason,
            )

        if role_key != "tabib":
            return RoleAction(
                actor_id=actor_id,
                action_type="heal",
                target_id=target_id,
                reason="Bu harakat faqat Tabibga tegishli.",
            )

        memory = self.get_memory(actor_id)

        previous_target = memory.last_target.get(str(actor_id))

        if previous_target == target_id:
            return RoleAction(
                actor_id=actor_id,
                action_type="heal",
                target_id=target_id,
                reason="Tabib bir odamni ketma-ket ikki tun davolay olmaydi.",
            )

        memory.last_target[str(actor_id)] = target_id

        return RoleAction(
            actor_id=actor_id,
            action_type="heal",
            target_id=target_id,
            success=True,
            reason="Davolash tayyorlandi.",
        )

    # =========================================================
    # 👁️ KUZATUVCHI
    # =========================================================

    def obser
