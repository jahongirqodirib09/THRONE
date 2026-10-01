from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from game_state import GameState
from role_engine import RoleAction, RoleEngine


@dataclass
class ResolutionResult:
    """Bir tun yoki bosqich yakunining natijasi."""

    deaths: list[int] = field(default_factory=list)
    saved: list[int] = field(default_factory=list)
    blocked: list[int] = field(default_factory=list)
    investigations: dict[int, dict] = field(default_factory=dict)
    observations: dict[int, list[int]] = field(default_factory=dict)
    stolen_gold: dict[int, int] = field(default_factory=dict)

    messages: list[str] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)


@dataclass
class PendingAttack:
    """Resolver ichidagi vaqtinchalik hujum."""

    attacker_id: int
    target_id: int

    attack_type: str = "ordinary"
    strong: bool = False
    bypass_ordinary_defense: bool = False
    bypass_special_defense: bool = False
    hidden: bool = False


class GameResolver:
    """
    THRONE o'yinining yakuniy harakat resolveri.

    Asosiy tartib:

    1. Bloklar
    2. Himoyalar
    3. Tekshiruvlar
    4. Iqtisodiy harakatlar
    5. Hujumlar
    6. Maxsus himoyalar
    7. O'lim / omon qolish
    8. Natijalarni qaytarish
    """

    ORDINARY_ATTACKS = {
        "qotil",
        "bosh_qomondon",
        "ovchi",
    }

    STRONG_ATTACKS = {
        "dushman_qomondoni",
        "dushman_suiqasddchisi",
    }

    HIDDEN_ATTACKS = {
        "suiqasddchi",
    }

    def __init__(self, role_engine: Optional[RoleEngine] = None):
        self.role_engine = role_engine or RoleEngine()

        # Har bir guruh uchun vaqtinchalik tun ma'lumotlari.
        self.pending_attacks: dict[int, list[PendingAttack]] = {}

        # Har bir guruhdagi bir martalik maxsus himoyalar.
        self.special_saves: dict[int, set[int]] = {}

    # =========================================================
    # GURUH XOTIRASI
    # =========================================================

    def _group_attacks(self, group_id: int) -> list[PendingAttack]:
        return self.pending_attacks.setdefault(group_id, [])

    def _group_saves(self, group_id: int) -> set[int]:
        return self.special_saves.setdefault(group_id, set())

    def clear_group(self, group_id: int) -> None:
        self.pending_attacks.pop(group_id, None)
        self.special_saves.pop(group_id, None)

    # =========================================================
    # HARAKATLARNI OLISH
    # =========================================================

    def collect_actions(
        self,
        game: GameState,
    ) -> list[RoleAction]:
        """
        GameState ichidagi tungi harakatlarni RoleAction
        ko'rinishiga o'tkazadi.
        """

        actions: list[RoleAction] = []

        for actor_id, action_data in game.night_actions.items():
            if not isinstance(action_data, dict):
                continue

            action_type = action_data.get("action_type")

            if not action_type:
                continue

            actions.append(
                RoleAction(
                    actor_id=actor_id,
                    action_type=action_type,
                    target_id=action_data.get("target_id"),
                    value=action_data.get("value", 0),
                    success=action_data.get("success", True),
                    blocked=action_data.get("blocked", False),
                    reason=action_data.get("reason", ""),
                    metadata=action_data.get("metadata", {}),
                )
            )

        return actions

    # =========================================================
    # TUNNI HAL QILISH
    # =========================================================

    def resolve_night(
        self,
        game: GameState,
        actions: Optional[list[RoleAction]] = None,
    ) -> ResolutionResult:

        result = ResolutionResult()

        if not game.is_active():
            result.messages.append(
                "O'yin faol emas."
            )
            return result

        if actions is None:
            actions = self.collect_actions(game)

        group_id = game.group_id

        self.pending_attacks[group_id] = []

        # Har bir tun uchun vaqtinchalik himoyalar tozalanadi.
        self.role_engine.clear_game_memory()

        # -----------------------------------------------------
        # 1. BLOKLAR
        # -----------------------------------------------------

        blocked_actions: set[int] = set()

        for action in actions:
            if action.action_type != "block":
                continue

            if not action.success:
                continue

            if action.target_id is None:
                continue

            blocked_actions.add(action.target_id)

            result.blocked.append(action.target_id)

            result.events.append(
                {
                    "type": "block",
                    "actor_id": action.actor_id,
                    "target_id": action.target_id,
                }
            )

        # -----------------------------------------------------
        # 2. HIMoyalar
        # -----------------------------------------------------

        protected: set[int] = set()

        for action in actions:
            if action.action_type not in {
                "protect",
                "guard",
            }:
                continue

            if not action.success:
                continue

            if action.actor_id in blocked_actions:
                continue

            if action.target_id is None:
                continue

            protected.add(action.target_id)

            result.events.append(
                {
                    "type": "protection",
                    "actor_id": action.actor_id,
                    "target_id": action.target_id,
                }
            )

        # -----------------------------------------------------
        # 3. TEKSHIRUVLAR
        # -----------------------------------------------------

        for action in actions:
            if action.action_type != "investigate":
                continue

            if not action.success:
                continue

            if action.actor_id in blocked_actions:
                continue

            if action.target_id is None:
                continue

            result.investigations[action.actor_id] = {
                "target_id": action.target_id,
                "result": action.metadata.get(
                    "result",
                    "noma'lum",
                ),
                "target_role": action.metadata.get(
                    "target_role"
                ),
            }

            result.events.append(
                {
                    "type": "investigation",
                    "actor_id": action.actor_id,
                    "target_id": action.target_id,
                }
            )

        # -----------------------------------------------------
        # 4. KUZATUV
        # -----------------------------------------------------

        for action in actions:
            if action.action_type != "observe":
                continue

            if not action.success:
                continue

            if action.actor_id in blocked_actions:
                continue

            if action.target_id is None:
                continue

            visited = self._find_visitors(
                actions,
                action.target_id,
            )

            result.observations[action.actor_id] = visited

            result.events.append(
                {
                    "type": "observation",
                    "actor_id": action.actor_id,
                    "target_id": action.target_id,
                    "visitors": visited,
                }
            )

        # -----------------------------------------------------
        # 5. QAROQI
        # -----------------------------------------------------

        for action in actions:
            if action.action_type != "steal_gold":
                continue

            if not action.success:
                continue

            if action.actor_id in blocked_actions:
                continue

            if action.target_id is None:
                continue

            amount = max(0, action.value)

            if amount <= 0:
                continue

            result.stolen_gold[action.actor_id] = (
                result.stolen_gold.get(action.actor_id, 0)
                + amount
            )

            result.events.append(
                {
                    "type": "gold_steal",
                    "actor_id": action.actor_id,
                    "target_id": action.target_id,
                    "amount": amount,
                }
            )

        # -----------------------------------------------------
        # 6. DAVOLASH
        # -----------------------------------------------------

        healed: set[int] = set()

        for action in actions:
            if action.action_type != "heal":
                continue

            if not action.success:
                continue

            if action.actor_id in blocked_actions:
                continue

            if action.target_id is None:
                continue

            healed.add(action.target_id)

            result.events.append(
                {
                    "type": "heal",
                    "actor_id": action.actor_id,
                    "target_id": action.target_id,
                }
            )

        # -----------------------------------------------------
        # 7. HUJUMLARNI YIG'ISH
        # -----------------------------------------------------

        for action in actions:
            if action.action_type not in {
                "attack",
                "hidden_attack",
            }:
                continue

            if not action.success:
                continue

            if action.actor_id in blocked_actions:
                continue

            if action.target_id is None:
                continue

            attack = self._make_attack(
                game,
                action,
            )

            if attack is None:
                continue

            self._group_attacks(group_id).append(attack)

        # -----------------------------------------------------
        # 8. DUSHMAN QIROLI BYPASS
        # -----------------------------------------------------

        bypass_users: set[int] = set()

        for action in actions:
            if action.action_type != "attack_bypass":
                continue

            if not action.success:
                continue

            if action.actor_id in blocked_actions:
                continue

            bypass_users.add(action.actor_id)

        if bypass_users:
            for attack in self._group_attacks(group_id):
                if attack.attacker_id in bypass_users:
                    attack.bypass_ordinary_defense = True

        # -----------------------------------------------------
        # 9. HUJUMLARNI YECHISH
        # -----------------------------------------------------

        for attack in self._group_attacks(group_id):
            target_id = attack.target_id

            if target_id in healed:
                # Tabib targetni shu tun o'limdan saqlaydi.
                result.saved.append(target_id)

                result.events.append(
                    {
                        "type": "attack_healed",
                        "attacker_id": attack.attacker_id,
                        "target_id": target_id,
                    }
                )

                continue

            if attack.hidden:
                # Yashirin hujum oddiy hujum hisoblanadi.
                protected_by_normal = target_id in protected
            else:
                protected_by_normal = target_id in protected

            if (
                protected_by_normal
                and not attack.bypass_ordinary_defense
            ):
                result.saved.append(target_id)

                result.events.append(
                    {
                        "type": "attack_blocked_by_defense",
                        "attacker_id": attack.attacker_id,
                        "target_id": target_id,
                    }
                )

                continue

            # Kuchli hujum oddiy himoyani chetlab o'tadi,
            # lekin maxsus himoyalar keyin tekshiriladi.
            if attack.strong:
                special_saved = self._check_special_save(
                    game,
                    attack,
                    target_id,
                )

                if special_saved:
                    result.saved.append(target_id)

                    result.events.append(
                        {
                            "type": "strong_attack_special_save",
                            "attacker_id": attack.attacker_id,
                            "target_id": target_id,
                        }
                    )

                    continue

            # Oddiy hujum uchun maxsus bir martalik himoyalar.
            special_saved = self._check_special_save(
                game,
                attack,
                target_id,
            )

            if special_saved:
                result.saved.append(target_id)

                result.events.append(
                    {
                        "type": "special_save",
                        "attacker_id": attack.attacker_id,
                        "target_id": target_id,
                    }
                )

                continue

            # -------------------------------------------------
            # 10. O'LDIRISH
            # -------------------------------------------------

            player = game.get_player(target_id)

            if player is None or not player.alive:
                continue

            if target_id in result.deaths:
                continue

            player.alive = False

            result.deaths.append(target_id)

            result.events.append(
                {
                    "type": "death",
                    "attacker_id": attack.attacker_id,
                    "target_id": target_id,
                    "attack_type": attack.attack_type,
                    "hidden": attack.hidden,
                }
            )

        # -----------------------------------------------------
        # 11. NATIJA XABARLARI
        # -----------------------------------------------------

        self._build_result_messages(
            game,
            result,
        )

        # -----------------------------------------------------
        # 12. KEYINGI TUN UCHUN TOZALASH
        # -----------------------------------------------------

        self.role_engine.tick_cooldowns()

        game.clear_night_actions()

        self.pending_attacks[group_id] = []

        return result

    # =========================================================
    # HUJUM YARATISH
    # =========================================================

    def _make_attack(
        self,
        game: GameState,
        action: RoleAction,
    ) -> Optional[PendingAttack]:

        actor = game.get_player(action.actor_id)

        if actor is None:
            return None

        role_key = actor.role

        if role_key is None:
            return None

        attack_type = action.metadata.get(
            "attack_type",
            "ordinary",
        )

        bypass = bool(
            action.metadata.get(
                "bypass_defense",
                False,
            )
        )

        strong = role_key in self.STRONG_ATTACKS

        hidden = (
            role_key in self.HIDDEN_ATTACKS
            or action.action_type == "hidden_attack"
        )

        if role_key == "dushman_qomondoni":
            attack_type = "strong"

        if role_key == "dushman_suiqasddchisi":
            attack_type = "strong"

        if role_key == "bosh_qomondon":
            attack_type = "ordinary"

        if role_key == "qotil":
            attack_type = "ordinary"

        if role_key == "ovchi":
            attack_type = "ordinary"

        if role_key == "suiqasddchi":
            attack_type = "hidden"

        return PendingAttack(
            attacker_id=action.actor_id,
            target_id=action.target_id,
            attack_type=attack_type,
            strong=strong,
            bypass_ordinary_defense=bypass,
            bypass_special_defense=False,
            hidden=hidden,
        )

    # =========================================================
    # MAXSUS HIMOYALAR
    # =========================================================

    def _check_special_save(
        self,
        game: GameState,
        attack: PendingAttack,
        target_id: int,
    ) -> bool:

        target = game.get_player(target_id)

        if target is None:
            return False

        role_key = target.role

        if role_key is None:
            return False

        group_id = game.group_id
        saves = self._group_saves(group_id)

        # -----------------------------------------------------
        # 👑 SHOH
        # Birinchi oddiy tungi hujumdan omon qoladi.
        # -----------------------------------------------------

        if role_key == "shoh":
            if not attack.strong and not attack.hidden:
                if target_id not in saves:
                    saves.add(target_id)
                    return True

        # -----------------------------------------------------
        # 🤴 SHAHZODA
        # Shoh o'lganidan keyin birinchi oddiy hujum.
        # -----------------------------------------------------

        if role_key == "shahzoda":
            if not attack.strong:
                if target_id not in saves:
                    saves.add(target_id)
                    return True

        # -----------------------------------------------------
        # 🏰 RITSIR
        # Birinchi oddiy hujumdan zirh bilan omon qoladi.
        # -----------------------------------------------------

        if role_key == "ritsir":
            if not attack.strong and not attack.hidden:
                armor_key = target_id + 10_000_000

                if armor_key not in saves:
                    saves.add(armor_key)
                    return True

        # -----------------------------------------------------
        # 🤴 SURGUN SHAHZODA
        # Bir martalik o'zini saqlash.
        # -----------------------------------------------------

        if role_key == "surgun_shahzoda":
            if attack.target_id == target_id:
                save_key = target_id + 20_000_000

                if save_key not in saves:
                    saves.add(save_key)
                    return True

        # -----------------------------------------------------
        # 🛡️ QIROL QO'RIQCHISI
        # Dushman suiqasdchisini to'xtata oladi.
        # -----------------------------------------------------

        if role_key == "dushman_suiqasddchisi":
            return False

        attacker = game.get_player(attack.attacker_id)

        if attacker is not None:
            if (
                attacker.role == "dushman_suiqasddchisi"
                and target_id in self._protected_targets(
                    game
                )
            ):
                return True

        return False

    def _protected_targets(
        self,
        game: GameState,
    ) -> set[int]:

        targets: set[int] = set()

        for action in self.collect_actions(game):
            if action.action_type not in {
                "protect",
                "guard",
            }:
                continue

            if not action.success:
                continue

      
