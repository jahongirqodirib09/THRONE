from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from game_state import GamePhase, GameState
from role_engine import RoleAction, RoleEngine


@dataclass
class ActionResult:
    success: bool
    message: str
    action: Optional[RoleAction] = None
    data: dict[str, Any] | None = None


class GameActionManager:
    """
    THRONE o'yinchilarining amaliy harakatlarini boshqaradi.

    Bu fayl:
    - o'yinchi tirikligini tekshiradi
    - o'yin boshlanganini tekshiradi
    - fazani tekshiradi
    - rolga mos harakatni RoleEngine'ga yuboradi
    - harakat natijasini qaytaradi

    Yakuniy o'lim, g'alaba va mukofotlarni
    game_resolver.py boshqaradi.
    """

    NIGHT_ACTIONS = {
        "block",
        "protect",
        "investigate",
        "attack",
        "steal_gold",
        "heal",
        "observe",
        "guard",
        "memory_check",
        "hidden_attack",
        "shadow_mask",
        "attack_bypass",
    }

    DAY_ACTIONS = {
        "vote",
        "trade",
        "final_words",
    }

    def __init__(self, role_engine: Optional[RoleEngine] = None):
        self.role_engine = role_engine or RoleEngine()

    # =========================================================
    # UMUMIY TEKSHIRUV
    # =========================================================

    @staticmethod
    def _get_player(
        game: GameState,
        user_id: int,
    ):
        return game.get_player(user_id)

    @classmethod
    def _check_player(
        cls,
        game: GameState,
        user_id: int,
    ) -> tuple[bool, str]:

        player = cls._get_player(game, user_id)

        if player is None:
            return False, "Siz bu o'yinda mavjud emassiz."

        if not player.joined:
            return False, "Siz o'yindan chiqib ketgansiz."

        if not player.alive:
            return False, "Siz vafot etgansiz."

        return True, ""

    @staticmethod
    def _players(game: GameState) -> dict:
        return game.players

    # =========================================================
    # FAZA TEKSHIRUVI
    # =========================================================

    @staticmethod
    def _require_night(game: GameState) -> tuple[bool, str]:
        if not game.is_active():
            return False, "O'yin faol emas."

        if game.phase != GamePhase.NIGHT:
            return False, "Bu harakat faqat tunda bajariladi."

        return True, ""

    @staticmethod
    def _require_day(game: GameState) -> tuple[bool, str]:
        if not game.is_active():
            return False, "O'yin faol emas."

        if game.phase != GamePhase.DAY:
            return False, "Bu harakat faqat kunduzgi bosqichda bajariladi."

        return True, ""

    @staticmethod
    def _require_voting(game: GameState) -> tuple[bool, str]:
        if not game.is_active():
            return False, "O'yin faol emas."

        if game.phase != GamePhase.VOTING:
            return False, "Hozir ovoz berish vaqti emas."

        return True, ""

    # =========================================================
    # ROLNI TEKSHIRISH
    # =========================================================

    @staticmethod
    def _role_key(game: GameState, user_id: int) -> Optional[str]:
        player = game.get_player(user_id)

        if player is None:
            return None

        return player.role

    @classmethod
    def _require_role(
        cls,
        game: GameState,
        user_id: int,
        expected_role: str,
    ) -> tuple[bool, str]:

        role_key = cls._role_key(game, user_id)

        if role_key != expected_role:
            return False, "Bu qobiliyat sizning rolingizga tegishli emas."

        return True, ""

    # =========================================================
    # 🔒 BLOKLASH
    # =========================================================

    def block(
        self,
        game: GameState,
        actor_id: int,
        target_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        role_key = self._role_key(game, actor_id)

        if role_key not in {
            "shoh",
            "sehrgar",
            "qorovul",
        }:
            return ActionResult(
                False,
                "Sizda bloklash qobiliyati mavjud emas.",
            )

        action = self.role_engine.block_action(
            actor_id=actor_id,
            target_id=target_id,
            role_key=role_key,
            players=self._players(game),
        )

        return self._result_from_action(action)

    # =========================================================
    # 🛡️ HIMOYA
    # =========================================================

    def protect(
        self,
        game: GameState,
        actor_id: int,
        target_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        role_key = self._role_key(game, actor_id)

        allowed_roles = {
            "malika",
            "qirol_qoriqchisi",
            "ritsir",
        }

        if role_key not in allowed_roles:
            return ActionResult(
                False,
                "Sizda himoya qobiliyati mavjud emas.",
            )

        action = self.role_engine.protect(
            actor_id=actor_id,
            target_id=target_id,
            role_key=role_key,
            players=self._players(game),
        )

        return self._result_from_action(action)

    # =========================================================
    # 🔎 TEKSHIRUV
    # =========================================================

    def investigate(
        self,
        game: GameState,
        actor_id: int,
        target_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        role_key = self._role_key(game, actor_id)

        if role_key not in {
            "vazir",
            "aygoqchi",
        }:
            return ActionResult(
                False,
                "Sizda bu tekshiruv qobiliyati mavjud emas.",
            )

        action = self.role_engine.investigate(
            actor_id=actor_id,
            target_id=target_id,
            role_key=role_key,
            players=self._players(game),
        )

        return self._result_from_action(action)

    # =========================================================
    # 🎭 SOXTA MASLAHATCHI
    # =========================================================

    def activate_fake_check(
        self,
        game: GameState,
        actor_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_role(
            game,
            actor_id,
            "soxta_maslahatchi",
        )

        if not ok:
            return ActionResult(False, message)

        action = self.role_engine.activate_fake_check(
            actor_id=actor_id,
            role_key="soxta_maslahatchi",
            players=self._players(game),
        )

        return self._result_from_action(action)

    # =========================================================
    # 🌑 SOYA BOSHLIG'I — QORA NIQOB
    # =========================================================

    def activate_shadow_mask(
        self,
        game: GameState,
        actor_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_role(
            game,
            actor_id,
            "soya_boshligi",
        )

        if not ok:
            return ActionResult(False, message)

        action = self.role_engine.activate_shadow_mask(
            actor_id=actor_id,
            role_key="soya_boshligi",
        )

        return self._result_from_action(action)

    # =========================================================
    # ⚔️ HUJUM
    # =========================================================

    def attack(
        self,
        game: GameState,
        actor_id: int,
        target_id: int,
        *,
        attack_type: str = "ordinary",
        bypass_defense: bool = False,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        role_key = self._role_key(game, actor_id)

        attack_roles = {
            "qotil",
            "bosh_qomondon",
            "ovchi",
            "dushman_qomondoni",
            "dushman_suiqasddchisi",
            "suiqasddchi",
            "soya_boshligi",
        }

        if role_key not in attack_roles:
            return ActionResult(
                False,
                "Sizda hujum qobiliyati mavjud emas.",
            )

        action = self.role_engine.attack(
            actor_id=actor_id,
            target_id=target_id,
            role_key=role_key,
            players=self._players(game),
            attack_type=attack_type,
            bypass_defense=bypass_defense,
        )

        return self._result_from_action(action)

    # =========================================================
    # 👑 DUSHMAN QIROLI
    # =========================================================

    def activate_attack_bypass(
        self,
        game: GameState,
        actor_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_role(
            game,
            actor_id,
            "dushman_qiroli",
        )

        if not ok:
            return ActionResult(False, message)

        action = self.role_engine.activate_attack_bypass(
            actor_id=actor_id,
            role_key="dushman_qiroli",
        )

        return self._result_from_action(action)

    # =========================================================
    # 💰 QAROQI
    # =========================================================

    def steal_gold(
        self,
        game: GameState,
        actor_id: int,
        target_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_role(
            game,
            actor_id,
            "qaroqi",
        )

        if not ok:
            return ActionResult(False, message)

        action = self.role_engine.steal_gold(
            actor_id=actor_id,
            target_id=target_id,
            players=self._players(game),
        )

        return self._result_from_action(action)

    # =========================================================
    # 🩺 TABIB
    # =========================================================

    def heal(
        self,
        game: GameState,
        actor_id: int,
        target_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_role(
            game,
            actor_id,
            "tabib",
        )

        if not ok:
            return ActionResult(False, message)

        action = self.role_engine.heal(
            actor_id=actor_id,
            target_id=target_id,
            role_key="tabib",
            players=self._players(game),
        )

        return self._result_from_action(action)

    # =========================================================
    # 👁️ KUZATUVCHI
    # =========================================================

    def observe(
        self,
        game: GameState,
        actor_id: int,
        target_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_role(
            game,
            actor_id,
            "kuzatuvchi",
        )

        if not ok:
            return ActionResult(False, message)

        action = self.role_engine.observe(
            actor_id=actor_id,
            target_id=target_id,
            role_key="kuzatuvchi",
            players=self._players(game),
        )

        return self._result_from_action(action)

    # =========================================================
    # 🔒 QOROVUL
    # =========================================================

    def guard(
        self,
        game: GameState,
        actor_id: int,
        target_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_role(
            game,
            actor_id,
            "qorovul",
        )

        if not ok:
            return ActionResult(False, message)

        action = self.role_engine.guard(
            actor_id=actor_id,
            target_id=target_id,
            role_key="qorovul",
            players=self._players(game),
        )

        return self._result_from_action(action)

    # =========================================================
    # 📜 SOLNOMACHI
    # =========================================================

    def memory_check(
        self,
        game: GameState,
        actor_id: int,
        event: Optional[dict],
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_role(
            game,
            actor_id,
            "solnomachi",
        )

        if not ok:
            return ActionResult(False, message)

        action = self.role_engine.memory_check(
            actor_id=actor_id,
            event=event,
        )

        return self._result_from_action(action)

    # =========================================================
    # 💰 SAVDOGAR
    # =========================================================

    def trade(
        self,
        game: GameState,
        actor_id: int,
        target_id: int,
        give_type: str,
        give_amount: int,
        receive_type: str,
        receive_amount: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_day(game)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_role(
            game,
            actor_id,
            "savdogar",
        )

        if not ok:
            return ActionResult(False, message)

        action = self.role_engine.trade(
            actor_id=actor_id,
            target_id=target_id,
            give_type=give_type,
            give_amount=give_amount,
            receive_type=receive_type,
            receive_amount=receive_amount,
            players=self._players(game),
        )

        return self._result_from_action(action)

    # =========================================================
    # 🗡️ YASHIRIN SUIQASD
    # =========================================================

    def hidden_attack(
        self,
        game: GameState,
        actor_id: int,
        target_id: int,
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_night(game)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_role(
            game,
            actor_id,
            "suiqasddchi",
        )

        if not ok:
            return ActionResult(False, message)

        action = self.role_engine.hidden_attack(
            actor_id=actor_id,
            target_id=target_id,
            role_key="suiqasddchi",
            players=self._players(game),
        )

        return self._result_from_action(action)

    # =========================================================
    # 🗳️ OVOZ
    # =========================================================

    def vote(
        self,
        game: GameState,
        actor_id: int,
        target_id: Optional[int],
    ) -> ActionResult:

        ok, message = self._check_player(game, actor_id)
        if not ok:
            return ActionResult(False, message)

        ok, message = self._require_voting(game)
        if not ok:
            return ActionResult(False, message)

        # game_state.py ichidagi adolatli ovoz tizimi ishlaydi.
        registered = game.register_vote(
            voter_id=actor_id,
            target_id=target_id,
        )

        if not registered:
            return ActionResult(
                False,
                "Ovoz berish amalga oshmadi. Balki siz allaqachon ovoz bergandirsiz.",
            )

        if target_id is None:
            return ActionResult(
                True,
                "🚫 Siz ovoz bermaslikni tanladingiz.",
                data={
                    "voter_id": actor_id,
                    "target_id": None,
                },
            )

        target = game.get_player(target_id)

        target_name = (
            target.name
            if target is not None
            else "Noma'lum o'yinchi"
        )

        return ActionResult(
            True,
            f"🗳️ Siz {target_name} uchun ovoz berdingiz.",
            data={
                "voter_id": actor_id,
                "target_id": target_id,
            },
        )

    # =========================================================
    # 📜 YAKUNIY SO'Z
    # =========================================================

    def final_words(
        self,
        game: GameState,
        actor_id: int,
        text: str,
    ) -> ActionResult:

        player = game.get_player(actor_id)

        if player is None:
            return ActionResult(
                False,
                "O'yinchi topilmadi.",
            )

        if player.alive:
            return ActionResult(
                False,
                "Tirik o'yinchi yakuniy so'z bera olmaydi.",
            )

        if player.final_words_given:
            return ActionResult(
   
