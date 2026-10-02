from __future__ import annotations

import random
import time

from config import (
    DEFAULT_DAY_TIME,
    DEFAULT_NIGHT_TIME,
    DEFAULT_VOTE_TIME,
    MAX_PLAYERS,
    MIN_PLAYERS,
)
from game_state import GamePhase, GameState, PlayerState
from roles import ROLE_MAP, TEAM_ROLES, get_role


class GameEngine:
    """THRONE o‘yinining asosiy boshqaruv qismi."""

    def __init__(self, chat_id: int):
        self.state = GameState(chat_id=chat_id)

    # =========================================================
    # LOBBY
    # =========================================================

    def add_player(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str = "",
    ) -> bool:
        """O‘yinchini lobbyga qo‘shadi."""

        if self.state.phase != GamePhase.LOBBY:
            return False

        if self.state.player_count() >= MAX_PLAYERS:
            return False

        return self.state.add_player(
            user_id=user_id,
            username=username,
            first_name=first_name,
        )

    def remove_player(self, user_id: int) -> bool:
        """Lobbydagi o‘yinchini chiqaradi."""

        if self.state.phase != GamePhase.LOBBY:
            return False

        return self.state.remove_player(user_id)

    def can_start(self) -> bool:
        """O‘yin boshlash uchun yetarli o‘yinchi bormi?"""

        return (
            self.state.phase == GamePhase.LOBBY
            and self.state.player_count() >= MIN_PLAYERS
        )

    def start_countdown(self) -> bool:
        """O‘yin boshlanish countdownini ishga tushiradi."""

        if not self.can_start():
            return False

        self.state.countdown_started = True
        return True

    # =========================================================
    # ROLE ASSIGNMENT
    # =========================================================

    def assign_roles(self) -> bool:
        """O‘yinchilarga rollarni taqsimlaydi."""

        players = self.state.joined_players()

        if len(players) < MIN_PLAYERS:
            return False

        if len(players) > len(ROLE_MAP):
            return False

        role_ids = self._build_role_pool(len(players))

        if len(role_ids) != len(players):
            return False

        random.shuffle(role_ids)

        for player, role_id in zip(players, role_ids):
            role = get_role(role_id)

            if role is None:
                return False

            self.state.set_role(
                user_id=player.user_id,
                role_id=role_id,
                team=role["team"],
            )

        return True

    def _build_role_pool(self, player_count: int) -> list[str]:
        """
        O‘yinchilar soniga qarab rol havzasini tuzadi.

        Birinchi test versiyasida barcha rollarni birdan
        ishlatmaymiz. Kuchli rollar soni ham nazorat qilinadi.
        """

        if player_count < MIN_PLAYERS:
            return []

        # Kichik o‘yin uchun asosiy rollar.
        base_roles = [
            "shoh",
            "vazir",
            "qirol_qoriqchisi",
            "qotil",
            "josus",
            "ovchi",
            "tabib",
            "sayyoh",
        ]

        # O‘yin kattalashgani sari qo‘shimcha rollar.
        additional_roles = [
            "malika",
            "shahzoda",
            "bosh_qomondon",
            "qozi",
            "xazinachi",
            "ritsar",
            "aygoqchi",
            "soya_boshligi",
            "soxta_maslahatchi",
            "xoin",
            "qora_vazir",
            "dushman_qiroli",
            "dushman_qomondoni",
            "dushman_josusi",
            "dushman_suiqasdchisi",
            "telba",
            "yollanma_jangchi",
            "surgun_shahzoda",
            "taxt_davogari",
            "qaroqchi",
            "kuzatuvchi",
            "qorovul",
            "solnomachi",
            "savdogar",
            "suiqasdchi",
            "oshpaz",
            "xizmatkor",
            "tinch_aholi",
        ]

        pool: list[str] = []

        # Avval bazaviy rollar ichidan mavjudlarini olamiz.
        for role_id in base_roles:
            if role_id in ROLE_MAP:
                pool.append(role_id)

            if len(pool) >= player_count:
                break

        # Yetmasa qo‘shimcha rollardan to‘ldiramiz.
        if len(pool) < player_count:
            for role_id in additional_roles:
                if role_id not in pool and role_id in ROLE_MAP:
                    pool.append(role_id)

                if len(pool) >= player_count:
                    break

        return pool[:player_count]

    # =========================================================
    # GAME START
    # =========================================================

    def start_game(self) -> bool:
        """Lobbydan haqiqiy o‘yinga o‘tadi."""

        if not self.can_start():
            return False

        if not self.assign_roles():
            return False

        self.state.countdown_started = False
        self.state.finished = False

        self.state.set_phase(
            GamePhase.NIGHT,
            started_at=time.time(),
            ends_at=time.time() + DEFAULT_NIGHT_TIME,
        )

        self.state.reset_night_actions()
        self.state.clear_events()

        self.state.add_event(
            "game_started",
            chat_id=self.state.chat_id,
            player_count=self.state.player_count(),
        )

        return True

    # =========================================================
    # PHASES
    # =========================================================

    def start_night(self) -> bool:
        """Yangi tunni boshlaydi."""

        if self.state.finished:
            return False

        self.state.set_phase(
            GamePhase.NIGHT,
            started_at=time.time(),
            ends_at=time.time() + DEFAULT_NIGHT_TIME,
        )

        self.state.reset_night_actions()
        self.state.clear_events()

        return True

    def start_day(self) -> bool:
        """Kunni boshlaydi."""

        if self.state.finished:
            return False

        self.state.set_phase(
            GamePhase.DAY,
            started_at=time.time(),
            ends_at=time.time() + DEFAULT_DAY_TIME,
        )

        self.state.reset_day_actions()

        return True

    def start_voting(self) -> bool:
        """Ovoz berish bosqichini boshlaydi."""

        if self.state.finished:
            return False

        self.state.set_phase(
            GamePhase.VOTING,
            started_at=time.time(),
            ends_at=time.time() + DEFAULT_VOTE_TIME,
        )

        self.state.reset_votes()

        return True

    # =========================================================
    # VOTING
    # =========================================================

    def vote(
        self,
        voter_id: int,
        target_id: int,
    ) -> bool:
        """O‘yinchining ovozini qabul qiladi."""

        return self.state.add_vote(
            voter_id=voter_id,
            target_id=target_id,
        )

    def finish_voting(self) -> int | None:
        """
        Ovoz berishni tugatadi.

        Yagona eng ko‘p ovoz olgan o‘yinchi o‘ladi.
        Tenglik bo‘lsa hech kim chiqarilmaydi.
        """

        if self.state.phase != GamePhase.VOTING:
            return None

        target_id = self.state.most_voted_player()

        if target_id is None:
            self.start_night()
            return None

        target = self.state.get_player(target_id)

        if target is None or not target.alive:
            self.start_night()
            return None

        self.state.kill_player(target_id)

        self.state.add_event(
            "voted_out",
            user_id=target_id,
            role_id=target.role_id,
            team=target.team,
        )

        self.start_night()

        return target_id

    # =========================================================
    # NIGHT ACTIONS
    # =========================================================

    def submit_night_action(
        self,
        user_id: int,
        action_type: str,
        target_id: int | None = None,
        **extra,
    ) -> bool:
        """
        Kechasi rolning harakatini saqlaydi.

        Bu hozircha faqat actionni yig‘adi.
        Haqiqiy bloklash, himoya, tekshiruv, hujum va
        maxsus qobiliyatlar keyingi engine bosqichida ishlanadi.
        """

        player = self.state.get_player(user_id)

        if player is None:
            return False

        if not player.alive:
            return False

        if self.state.phase != GamePhase.NIGHT:
            return False

        if target_id is not None:
            target = self.state.get_player(target_id)

            if target is None or not target.alive:
                return False

        action = {
            "type": action_type,
            "target_id": target_id,
            **extra,
        }

        return self.state.set_night_action(
            user_id=user_id,
            action=action,
        )

    def finish_night(self) -> list[int]:
        """
        Tungi harakatlarni yakunlaydi.

        Hozirgi birinchi test versiyasida hujumlar
        alohida resolverga ulanadi. Shu sababli bu metod
        hali avtomatik ravishda barcha rollarni o‘ldirmaydi.
        """

        if self.state.phase != GamePhase.NIGHT:
            return []

        deaths: list[int] = []

        self.state.add_event(
            "night_finished",
            actions_count=len(self.state.night_actions),
        )

        self.start_day()

        return deaths

    # =========================================================
    # PLAYER INFORMATION
    # =========================================================

    def get_role_info(self, user_id: int) -> dict | None:
        """O‘yinchining rol ma'lumotini qaytaradi."""

        player = self.state.get_player(user_id)

        if player is None or player.role_id is None:
            return None

        return get_role(player.role_id)

    def get_teammates(self, user_id: int) -> list[PlayerState]:
        """
        O‘yinchining bir jamoasidagi tirik sheriklarini qaytaradi.

        Keyinchalik rolga qarab maxsus sheriklik qoidalari
        qo‘shiladi.
        """

        player = self.state.get_player(user_id)

        if player is None or player.team is None:
            return []

        return [
            other
            for other in self.state.alive_players()
            if other.user_id != user_id
            and other.team == player.team
        ]

    def get_alive_player_ids(self) -> list[int]:
        """Tirik o‘yinchilar IDlari."""

        return [
            player.user_id
            for player in self.state.alive_players()
        ]

    # =========================================================
    # GAME RESULT
    # =========================================================

    def check_winner(self) -> str | None:
        """
        Asosiy jamoaviy g‘alaba tekshiruvi.

        Bu yakuniy victory system emas.
        Keyinchalik YAKKA rollarining alohida g‘alaba
        shartlari shu yerga qo‘shiladi.
        """

        alive = self.state.alive_players()

        if not alive:
            return "NONE"

        teams = {
            player.team
            for player in alive
            if player.team is not None
        }

        # KRON va SOYA qolmagan holatlar.
        if "KRON" not in teams and "SOYA" not in teams:
            return self._check_remaining_teams(teams)

        if "KRON" not in teams:
            if "SOYA" in teams:
                return "SOYA"

        if "SOYA" not in teams:
            if "KRON" in teams:
                return "KRON"

        return None

    def _check_remaining_teams(
        self,
        teams: set[str],
    ) -> str | None:
        """KRON/SOYA qolmagan vaziyat uchun tekshiruv."""

        if len(teams) == 1:
            return next(iter(teams))

        if "YAKKA" in teams and len(teams) == 1:
            return "YAKKA"

        if "LEGION" in teams and len(teams) == 1:
            return "LEGION"

        return None

    def finish_game(self, winner_team: str) -> None:
        """O‘yinni yakunlaydi."""

        self.state.set_winner(winner_team)

        self.state.add_event(
            "game_finished",
            winner_team=winner_team,
        )

    # =========================================================
    # UTILITY
    # =========================================================

    def is_finished(self) -> bool:
        """O‘yin tugaganmi?"""

        return self.state.finished

    def current_phase(self) -> GamePhase:
        """Hozirgi bosqich."""

        return self.state.phase

    def time_left(self) -> int:
        """Bosqich tugashigacha qolgan soniyalar."""

        if self.state.phase_ends_at is None:
            return 0

        remaining = self.state.phase_ends_at - time.time()

        return max(0, int(remaining))

    def player_name(self, user_id: int) -> str:
        """Telegramda ko‘rsatish uchun o‘yinchi nomi."""

        player = self.state.get_player(user_id)

        if player is None:
            return "Noma'lum o‘yinchi"

        if player.first_name:
            return player.first_name

        if player.username:
            return f"@{player.username}"

        return str(player.user_id)


def create_game(chat_id: int) -> GameEngine:
    """Yangi THRONE o‘yini yaratadi."""

    return GameEngine(chat_id)
