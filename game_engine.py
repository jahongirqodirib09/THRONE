from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from config import (
    DEFAULT_DAY_TIME,
    DEFAULT_GAME_START_TIME,
    DEFAULT_NIGHT_TIME,
    DEFAULT_VOTE_TIME,
    MAX_PLAYERS,
    MIN_PLAYERS,
)

from game_resolver import GameResolver, ResolutionResult
from game_state import GamePhase, GameState
from roles import (
    ROLES,
    Side,
    all_roles,
    get_role,
)


@dataclass
class StartResult:
    success: bool
    message: str
    game: Optional[GameState] = None


@dataclass
class PhaseResult:
    success: bool
    message: str
    phase: Optional[GamePhase] = None
    resolution: Optional[ResolutionResult] = None


class GameEngine:
    """
    THRONE asosiy o'yin dvigateli.

    Vazifalari:
    - o'yin yaratish
    - o'yinchilarni qo'shish/chiqarish
    - o'yinni boshlash
    - rollarni taqsimlash
    - tun/kunduz/ovoz bosqichlarini almashtirish
    - tungi harakatlarni resolverga berish
    - ovoz natijasini hisoblash
    - g'alaba shartini tekshirish

    Telegram xabarlarini yuborish bu faylning vazifasi emas.
    """

    def __init__(
        self,
        resolver: Optional[GameResolver] = None,
    ):
        self.games: dict[int, GameState] = {}

        self.resolver = resolver or GameResolver()

    # =========================================================
    # O'YINNI OLISH
    # =========================================================

    def get_game(
        self,
        group_id: int,
    ) -> Optional[GameState]:

        return self.games.get(group_id)

    def has_active_game(
        self,
        group_id: int,
    ) -> bool:

        game = self.games.get(group_id)

        return bool(
            game is not None
            and game.is_active()
        )

    # =========================================================
    # YANGI O'YIN
    # =========================================================

    def create_game(
        self,
        group_id: int,
        *,
        day_time: int = DEFAULT_DAY_TIME,
        vote_time: int = DEFAULT_VOTE_TIME,
        night_time: int = DEFAULT_NIGHT_TIME,
        start_time: int = DEFAULT_GAME_START_TIME,
    ) -> StartResult:

        existing = self.games.get(group_id)

        if existing is not None and not existing.ended:
            return StartResult(
                success=False,
                message="Bu guruhda allaqachon o'yin mavjud.",
            )

        game = GameState(
            group_id=group_id,
            day_time=max(10, day_time),
            vote_time=max(10, vote_time),
            night_time=max(10, night_time),
            start_time=max(5, start_time),
        )

        self.games[group_id] = game

        return StartResult(
            success=True,
            message="👑 Yangi THRONE o'yini yaratildi.",
            game=game,
        )

    # =========================================================
    # O'YINCHINI QO'SHISH
    # =========================================================

    def add_player(
        self,
        group_id: int,
        user_id: int,
        name: str,
        username: Optional[str] = None,
    ) -> tuple[bool, str]:

        game = self.games.get(group_id)

        if game is None:
            return False, "Avval o'yin yaratilishi kerak."

        if game.started:
            return False, "O'yin allaqachon boshlangan."

        if game.player_count() >= MAX_PLAYERS:
            return False, f"O'yinchilar soni {MAX_PLAYERS} taga yetdi."

        added = game.add_player(
            user_id=user_id,
            name=name,
            username=username,
        )

        if not added:
            return False, "Siz allaqachon o'yinga qo'shilgansiz."

        return (
            True,
            f"✅ {name} o'yinga qo'shildi.",
        )

    # =========================================================
    # O'YINDAN CHIQISH
    # =========================================================

    def remove_player(
        self,
        group_id: int,
        user_id: int,
    ) -> tuple[bool, str]:

        game = self.games.get(group_id)

        if game is None:
            return False, "O'yin topilmadi."

        player = game.get_player(user_id)

        if player is None:
            return False, "Siz o'yinda emassiz."

        removed = game.remove_player(user_id)

        if not removed:
            return False, "O'yindan chiqib bo'lmadi."

        return True, "🚪 O'yindan chiqdingiz."

    # =========================================================
    # STARTGA TAYYORLIK
    # =========================================================

    def can_start(
        self,
        group_id: int,
    ) -> tuple[bool, str]:

        game = self.games.get(group_id)

        if game is None:
            return False, "O'yin yaratilmagan."

        if game.started:
            return False, "O'yin allaqachon boshlangan."

        count = game.player_count()

        if count < MIN_PLAYERS:
            return (
                False,
                f"Kamida {MIN_PLAYERS} ta o'yinchi kerak. "
                f"Hozir: {count}.",
            )

        if count > MAX_PLAYERS:
            return (
                False,
                f"O'yinchilar soni {MAX_PLAYERS} tadan oshmasligi kerak.",
            )

        return True, ""

    # =========================================================
    # O'YINNI BOSHLASH
    # =========================================================

    def start_game(
        self,
        group_id: int,
    ) -> StartResult:

        game = self.games.get(group_id)

        if game is None:
            return StartResult(
                False,
                "O'yin topilmadi.",
            )

        can_start, reason = self.can_start(group_id)

        if not can_start:
            return StartResult(
                False,
                reason,
                game=game,
            )

        self._assign_roles(game)

        started = game.start_game()

        if not started:
            return StartResult(
                False,
                "O'yinni boshlash imkoni bo'lmadi.",
                game=game,
            )

        # Birinchi tun oldidan kun raqami 1 bo'ladi.
        game.day_number = 1

        game.phase = GamePhase.NIGHT

        return StartResult(
            True,
            "👑⚔️ THRONE boshlandi. Birinchi tun boshlandi.",
            game=game,
        )

    # =========================================================
    # ROLLARNI TAQSIMLASH
    # =========================================================

    def _assign_roles(
        self,
        game: GameState,
    ) -> None:

        players = [
            player
            for player in game.players.values()
            if player.joined
        ]

        count = len(players)

        role_keys = self._build_role_pool(count)

        random.shuffle(role_keys)
        random.shuffle(players)

        for player, role_key in zip(
            players,
            role_keys,
        ):
            player.role = role_key

            role = get_role(role_key)

            if role is not None:
                player.side = role.side.value
            else:
                player.side = None

    def _build_role_pool(
        self,
        player_count: int,
    ) -> list[str]:

        """
        O'yinchilar soniga qarab rollar havzasini yaratadi.

        36 rolning hammasini kichik o'yinga tiqmaymiz.
        O'yinchi ko'paygani sari rol tizimi kengayadi.
        """

        throne = self._roles_by_side(Side.THRONE)
        shadow = self._roles_by_side(Side.SHADOW)
        solo = self._roles_by_side(Side.SOLO)
        special = self._roles_by_side(Side.SPECIAL)

        # -----------------------------------------------------
        # 4 O'YINCHI
        # -----------------------------------------------------

        if player_count == 4:
            return [
                "shoh",
                "qotil",
                "ovchi",
                "tabib",
            ]

        # -----------------------------------------------------
        # 5 O'YINCHI
        # -----------------------------------------------------

        if player_count == 5:
            return [
                "shoh",
                "malika",
                "soya_boshligi",
                "qotil",
                "telba",
            ]

        # -----------------------------------------------------
        # 6 O'YINCHI
        # -----------------------------------------------------

        if player_count == 6:
            return [
                "shoh",
                "malika",
                "vazir",
                "soya_boshligi",
                "qotil",
                "ovchi",
            ]

        # -----------------------------------------------------
        # 7 O'YINCHI
        # -----------------------------------------------------

        if player_count == 7:
            return [
                "shoh",
                "malika",
                "vazir",
                "soya_boshligi",
                "qotil",
                "ovchi",
                "tabib",
            ]

        # -----------------------------------------------------
        # 8 O'YINCHI
        # -----------------------------------------------------

        if player_count == 8:
            return [
                "shoh",
                "malika",
                "vazir",
                "bosh_qomondon",
                "soya_boshligi",
                "qotil",
                "josus",
                "tabib",
            ]

        # -----------------------------------------------------
        # 9 O'YINCHI
        # -----------------------------------------------------

        if player_count == 9:
            return [
                "shoh",
                "malika",
                "vazir",
                "qirol_qoriqchisi",
                "soya_boshligi",
                "qotil",
                "josus",
                "ovchi",
                "tabib",
            ]

        # -----------------------------------------------------
        # 10+ O'YINCHI
        # -----------------------------------------------------

        pool: list[str] = []

        # Har qanday katta o'yinda kamida bitta Shoh.
        pool.append("shoh")

        # Taxt tomoni.
        throne_priority = [
            "malika",
            "shahzoda",
            "vazir",
            "bosh_qomondon",
            "qirol_qoriqchisi",
            "qazi",
            "xazinachi",
            "qishloq_aholisi",
            "xizmatkor",
            "ritsir",
            "aygoqchi",
        ]

        # Soya tomoni.
        shadow_priority = [
            "soya_boshligi",
            "qotil",
            "josus",
            "soxta_maslahatchi",
            "xoin",
            "qora_vazir",
            "dushman_qiroli",
            "dushman_qomondoni",
            "dushman_josusi",
            "dushman_suiqasddchisi",
        ]

        # Yakka tomoni.
        solo_priority = [
            "ovchi",
            "telba",
            "sayyoh",
            "yollanma_jangchi",
            "surgun_shahzoda",
            "taxt_davogari",
            "qaroqi",
        ]

        # Maxsus.
        special_priority = [
            "sehrgar",
            "tabib",
            "kuzatuvchi",
            "qorovul",
            "solnomachi",
            "savdogar",
            "suiqasddchi",
        ]

        for role_key in throne_priority:
            if len(pool) >= player_count:
                break

            if role_key in ROLES:
                pool.append(role_key)

        for role_key in shadow_priority:
            if len(pool) >= player_count:
                break

            if role_key in ROLES:
                pool.append(role_key)

        for role_key in solo_priority:
            if len(pool) >= player_count:
                break

            if role_key in ROLES:
                pool.append(role_key)

        for role_key in special_priority:
            if len(pool) >= player_count:
                break

            if role_key in ROLES:
                pool.append(role_key)

        # Agar kelajakda 36 dan ortiq o'yinchi kerak bo'lsa,
        # mavjud rollarni takrorlashga ruxsat bermaymiz.
        return pool[:player_count]

    @staticmethod
    def _roles_by_side(
        side: Side,
    ) -> list[str]:

        return [
            role.key
            for role in all_roles()
            if role.side == side
        ]

    # =========================================================
    # TUNNI BOSHLASH
    # =========================================================

    def start_night(
        self,
        group_id: int,
    ) -> PhaseResult:

        game = self.games.get(group_id)

        if game is None:
            return PhaseResult(
                False,
                "O'yin topilmadi.",
            )

        if not game.is_active():
            return PhaseResult(
                False,
                "O'yin faol emas.",
            )

        game.start_night()

        return PhaseResult(
            True,
            f"🌙 {game.day_number}-tun boshlandi.",
            phase=GamePhase.NIGHT,
        )

    # =========================================================
    # TUN HARAKATINI SAQLASH
    # =========================================================

    def register_night_action(
        self,
        group_id: int,
        user_id: int,
        action_type: str,
        *,
        target_id: Optional[int] = None,
        value: int = 0,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, str]:

        game = self.games.get(group_id)

        if game is None:
            return False, "O'yin topilmadi."

        if game.phase != GamePhase.NIGHT:
            return False, "Hozir tun emas."

        player = game.get_player(user_id)

        if player is None:
            return False, "Siz o'yinda emassiz."

        if not player.alive:
            return False, "Siz vafot etgansiz."

        if not player.joined:
            return False, "Siz o'yindan chiqib ketgansiz."

        if action_type not in {
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
        }:
            return False, "Noma'lum tungi harakat."

        action = {
            "action_type": action_type,
            "target_id": target_id,
            "value": value,
            "success": True,
            "metadata": metadata or {},
        }

        saved = game.set_night_action(
            user_id,
            action,
        )

        if not saved:
            return False, "Tungi harakat saqlanmadi."

        return True, "🌙 Tungi harakatingiz qabul qilindi."

    # =========================================================
    # TUNNI YAKUNLASH
    # =========================================================

    def resolve_night(
        self,
        group_id: int,
    ) -> PhaseResult:

        game = self.games.get(group_id)

        if game is None:
            return PhaseResult(
                False,
                "O'yin topilmadi.",
            )

        if game.phase != GamePhase.NIGHT:
            return PhaseResult(
                False,
                "Hozir tun bosqichi emas.",
            )

        resolution = self.resolver.resolve_night(
            game
        )

        # O'limlardan keyin g'alabani tekshiramiz.
        winner = self.check_winner(game)

        if winner is not None:
            game.end_game(winner)

            return PhaseResult(
                True,
                f"🏆 O'yin yakunlandi. G'olib tomon: {winner}",
                phase=GamePhase.ENDED,
                resolution=resolution,
            )

        game.next_day()

        return PhaseResult(
            True,
            f"☀️ {game.day_number}-kun boshlandi.",
            phase=GamePhase.DAY,
            resolution=resolution,
        )

    # =========================================================
    # KUNNI BOSHLASH
    # =========================================================

    def start_day(
        self,
        group_id: int,
    ) -> PhaseResult:

        game = self.games.get(group_id)

        if game is None:
            return PhaseResult(
                False,
                "O'yin topilmadi.",
            )

        if not game.is_active():
            return PhaseResult(
                False,
                "O'yin faol emas.",
            )

        game.phase = GamePhase.DAY

        return PhaseResult(
            True,
            f"☀️ {game.day_number}-kun boshlandi.",
            phase=GamePhase.DAY,
        )

    # =========================================================
    # OVOZ BERISHNI BOSHLASH
    # =========================================================

    def start_voting(
        self,
        group_id: int,
    ) -> PhaseResult:

        game = self.games.get(group_id)

        if game is None:
            return PhaseResult(
                False,
                "O'yin topilmadi.",
            )

        if not game.is_active():
            return PhaseResult(
                False,
                "O'yin faol emas.",
            )

        game.start_voting()

        return PhaseResult(
            True,
            "🗳️ Ovoz berish boshlandi.",
            phase=GamePhase.VOTING,
        )

    # =========================================================
    # OVOZNI SAQLASH
    # =========================================================

    def register_vote(
        self,
        group_id: int,
        voter_id: int,
        target_id: Optional[int],
    ) -> tuple[bool, str]:

        game = self.games.get(group_id)

        if game is None:
            return False, "O'yin topilmadi."

        if game.phase != GamePhase.VOTING:
            return False, "Hozir ovoz berish vaqti emas."

        voter = game.get_player(voter_id)

        if voter is None:
            return False, "Siz o'yinda emassiz."

        if not voter.alive:
            return False, "Vafot etgan o'yinchi ovoz bera olmaydi."

        if not voter.joined:
            return False, "Siz o'yindan chiqib ketgansiz."

        if voter.voted:
            return False, "Siz allaqachon ovoz bergansiz."

        if target_id is not None:
            target = game.get_player(target_id)

            if target is None:
                return False, "Nishon topilmadi."

            if not target.alive:
                return False, "Vafot etgan o'yinchiga ovoz berib bo'lmaydi."

            if not target.joined:
                return False, "Bu o'yinchi o'yinda emas."

        registered = game.register_vote(
            voter_id=voter_id,
            target_id=target_id,
        )

        if not registered:
            return False, "Ovoz qabul qilinmadi."

        return True, "🗳️ Ovoz qabul qilindi."

    # =========================================================
    # OVOZ NATIJASI
    # =========================================================

    def resolve_voting(
        self,
        group_id: int,
    ) -> PhaseResult:

        game = self.games.get(group_id)

        if game is None:
            return PhaseResult(
                False,
                "O'yin topilmadi.",
            )

        if game.phase != GamePhase.VOTING:
            return PhaseResult(
                False,
                "Hozir ovoz berish bosqichi emas.",
            )

        eliminated_id = game.voting_result()

        if eliminated_id is None:
            # Durang yoki hech kim ovoz bermagan.
            game.reset_votes()

            winner = self.check_winner(game)

            if winner is not None:
                game.end_
