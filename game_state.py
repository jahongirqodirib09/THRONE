from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GamePhase(str, Enum):
    """THRONE o‘yin bosqichlari."""

    LOBBY = "lobby"
    NIGHT = "night"
    DAY = "day"
    VOTING = "voting"
    ENDED = "ended"


@dataclass
class PlayerState:
    """Bitta o‘yinchining joriy o‘yindagi holati."""

    user_id: int
    username: str | None = None
    first_name: str = ""

    role_id: str | None = None
    team: str | None = None

    alive: bool = True
    joined: bool = True

    voted_for: int | None = None

    night_action_used: bool = False
    day_message_sent: bool = False

    inactivity_count: int = 0

    # Keyinchalik himoya, hujum va maxsus qobiliyatlar
    # shu maydon orqali boshqariladi.
    protection_used: bool = False
    escape_used: bool = False

    # Oshpaz kabi maxsus rollar uchun vaqtinchalik ma'lumotlar.
    temporary_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class GameState:
    """Bitta Telegram guruhidagi THRONE o‘yinining holati."""

    chat_id: int

    phase: GamePhase = GamePhase.LOBBY

    players: dict[int, PlayerState] = field(default_factory=dict)

    # Lobby va o‘yin vaqtlarini boshqarish uchun.
    phase_started_at: float | None = None
    phase_ends_at: float | None = None

    # O‘yin boshlanishidan oldingi countdown.
    countdown_started: bool = False

    # O‘yin tugagan yoki yo‘qligi.
    finished: bool = False

    # Ovozlar.
    votes: dict[int, int] = field(default_factory=dict)

    # Kechasi bajariladigan harakatlar.
    night_actions: dict[int, dict[str, Any]] = field(default_factory=dict)

    # Shu tun/kundagi muhim hodisalar.
    events: list[dict[str, Any]] = field(default_factory=list)

    # G‘olib tomon.
    winner_team: str | None = None

    # O‘yin uchun qo‘shimcha ma'lumotlar.
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_player(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str = "",
    ) -> bool:
        """O‘yinchining lobbyga qo‘shilishini ta'minlaydi."""

        if self.finished:
            return False

        if user_id in self.players:
            player = self.players[user_id]

            if username is not None:
                player.username = username

            if first_name:
                player.first_name = first_name

            player.joined = True
            return False

        self.players[user_id] = PlayerState(
            user_id=user_id,
            username=username,
            first_name=first_name,
        )

        return True

    def remove_player(self, user_id: int) -> bool:
        """O‘yinchi lobbydan yoki o‘yindan chiqariladi."""

        if user_id not in self.players:
            return False

        del self.players[user_id]
        self.votes.pop(user_id, None)
        self.night_actions.pop(user_id, None)

        return True

    def get_player(self, user_id: int) -> PlayerState | None:
        """O‘yinchini ID orqali qaytaradi."""

        return self.players.get(user_id)

    def alive_players(self) -> list[PlayerState]:
        """Tirik o‘yinchilar ro‘yxati."""

        return [
            player
            for player in self.players.values()
            if player.alive and player.joined
        ]

    def dead_players(self) -> list[PlayerState]:
        """O‘lgan o‘yinchilar ro‘yxati."""

        return [
            player
            for player in self.players.values()
            if not player.alive
        ]

    def joined_players(self) -> list[PlayerState]:
        """O‘yinga qo‘shilgan barcha o‘yinchilar."""

        return [
            player
            for player in self.players.values()
            if player.joined
        ]

    def player_count(self) -> int:
        """O‘yindagi jami o‘yinchilar soni."""

        return len(self.joined_players())

    def alive_count(self) -> int:
        """Tirik o‘yinchilar soni."""

        return len(self.alive_players())

    def kill_player(self, user_id: int) -> bool:
        """O‘yinchini o‘ldirilgan holatga o‘tkazadi."""

        player = self.get_player(user_id)

        if player is None or not player.alive:
            return False

        player.alive = False
        player.voted_for = None

        return True

    def revive_player(self, user_id: int) -> bool:
        """Kelajakdagi maxsus qobiliyatlar uchun tiriltirish."""

        player = self.get_player(user_id)

        if player is None or player.alive:
            return False

        player.alive = True
        return True

    def set_role(
        self,
        user_id: int,
        role_id: str,
        team: str,
    ) -> bool:
        """O‘yinchiga rol va jamoa beradi."""

        player = self.get_player(user_id)

        if player is None:
            return False

        player.role_id = role_id
        player.team = team

        return True

    def reset_votes(self) -> None:
        """Ovozlarni tozalaydi."""

        self.votes.clear()

        for player in self.players.values():
            player.voted_for = None

    def add_vote(
        self,
        voter_id: int,
        target_id: int,
    ) -> bool:
        """Ovoz qo‘shadi yoki mavjud ovozni yangilaydi."""

        voter = self.get_player(voter_id)
        target = self.get_player(target_id)

        if voter is None or target is None:
            return False

        if not voter.alive or not target.alive:
            return False

        if self.phase != GamePhase.VOTING:
            return False

        self.votes[voter_id] = target_id
        voter.voted_for = target_id

        return True

    def vote_counts(self) -> dict[int, int]:
        """Har bir o‘yinchiga berilgan ovozlar sonini hisoblaydi."""

        counts: dict[int, int] = {}

        for target_id in self.votes.values():
            target = self.get_player(target_id)

            if target is None or not target.alive:
                continue

            counts[target_id] = counts.get(target_id, 0) + 1

        return counts

    def most_voted_player(self) -> int | None:
        """Eng ko‘p ovoz olgan o‘yinchini qaytaradi.

        Tenglik bo‘lsa hech kim chiqarilmaydi.
        """

        counts = self.vote_counts()

        if not counts:
            return None

        highest = max(counts.values())

        winners = [
            user_id
            for user_id, count in counts.items()
            if count == highest
        ]

        if len(winners) != 1:
            return None

        return winners[0]

    def set_phase(
        self,
        phase: GamePhase,
        started_at: float | None = None,
        ends_at: float | None = None,
    ) -> None:
        """O‘yin bosqichini almashtiradi."""

        self.phase = phase
        self.phase_started_at = started_at
        self.phase_ends_at = ends_at

        if phase != GamePhase.VOTING:
            self.reset_votes()

        if phase != GamePhase.NIGHT:
            self.night_actions.clear()

    def set_night_action(
        self,
        user_id: int,
        action: dict[str, Any],
    ) -> bool:
        """O‘yinchining tungi harakatini saqlaydi."""

        player = self.get_player(user_id)

        if player is None or not player.alive:
            return False

        if self.phase != GamePhase.NIGHT:
            return False

        self.night_actions[user_id] = action
        player.night_action_used = True

        return True

    def get_night_action(
        self,
        user_id: int,
    ) -> dict[str, Any] | None:
        """O‘yinchining tungi harakatini qaytaradi."""

        return self.night_actions.get(user_id)

    def add_event(
        self,
        event_type: str,
        **data: Any,
    ) -> None:
        """O‘yinda sodir bo‘lgan hodisani saqlaydi."""

        self.events.append(
            {
                "type": event_type,
                **data,
            }
        )

    def clear_events(self) -> None:
        """Joriy bosqich hodisalarini tozalaydi."""

        self.events.clear()

    def reset_night_actions(self) -> None:
        """Tun harakatlarini keyingi tun uchun tozalaydi."""

        self.night_actions.clear()

        for player in self.players.values():
            player.night_action_used = False

    def reset_day_actions(self) -> None:
        """Kunlik harakatlarni tozalaydi."""

        for player in self.players.values():
            player.day_message_sent = False

    def mark_inactive(self, user_id: int) -> bool:
        """Faol bo‘lmagan o‘yinchining hisoblagichini oshiradi."""

        player = self.get_player(user_id)

        if player is None:
            return False

        player.inactivity_count += 1
        return True

    def reset_inactivity(self, user_id: int) -> bool:
        """O‘yinchining faollik hisoblagichini nolga qaytaradi."""

        player = self.get_player(user_id)

        if player is None:
            return False

        player.inactivity_count = 0
        return True

    def set_winner(self, team: str) -> None:
        """G‘olib jamoani belgilaydi."""

        self.winner_team = team
        self.finished = True
        self.phase = GamePhase.ENDED

    def reset_for_new_game(self) -> None:
        """Guruhda yangi o‘yin boshlash uchun holatni tozalaydi."""

        self.phase = GamePhase.LOBBY
        self.phase_started_at = None
        self.phase_ends_at = None

        self.players.clear()
        self.votes.clear()
        self.night_actions.clear()
        self.events.clear()

        self.winner_team = None
        self.finished = False
        self.countdown_started = False
        self.metadata.clear()
