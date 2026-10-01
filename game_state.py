from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GamePhase(str, Enum):
    WAITING = "waiting"
    STARTING = "starting"
    NIGHT = "night"
    DAY = "day"
    VOTING = "voting"
    ENDED = "ended"


@dataclass
class PlayerState:
    user_id: int
    name: str
    username: Optional[str] = None

    role: Optional[str] = None
    side: Optional[str] = None

    alive: bool = True
    joined: bool = True
    inactive_nights: int = 0

    final_words_given: bool = False
    voted: bool = False


@dataclass
class GameState:
    group_id: int

    phase: GamePhase = GamePhase.WAITING
    day_number: int = 0

    players: dict[int, PlayerState] = field(default_factory=dict)

    votes: dict[int, int] = field(default_factory=dict)

    night_actions: dict[int, dict] = field(default_factory=dict)

    day_time: int = 45
    vote_time: int = 45
    night_time: int = 60
    start_time: int = 30

    game_message_id: Optional[int] = None
    phase_message_id: Optional[int] = None

    started: bool = False
    ended: bool = False

    winner: Optional[str] = None

    def add_player(
        self,
        user_id: int,
        name: str,
        username: Optional[str] = None,
    ) -> bool:
        if self.started:
            return False

        if user_id in self.players:
            return False

        self.players[user_id] = PlayerState(
            user_id=user_id,
            name=name,
            username=username,
        )
        return True

    def remove_player(self, user_id: int) -> bool:
        if user_id not in self.players:
            return False

        if self.started:
            self.players[user_id].joined = False
            self.players[user_id].alive = False
        else:
            del self.players[user_id]

        return True

    def get_player(self, user_id: int) -> Optional[PlayerState]:
        return self.players.get(user_id)

    def alive_players(self) -> list[PlayerState]:
        return [
            player
            for player in self.players.values()
            if player.joined and player.alive
        ]

    def alive_count(self) -> int:
        return len(self.alive_players())

    def player_count(self) -> int:
        return len(
            [
                player
                for player in self.players.values()
                if player.joined
            ]
        )

    def kill_player(self, user_id: int) -> bool:
        player = self.players.get(user_id)

        if player is None or not player.alive:
            return False

        player.alive = False
        player.voted = False
        return True

    def reset_votes(self) -> None:
        self.votes.clear()

        for player in self.players.values():
            player.voted = False

    def register_vote(
        self,
        voter_id: int,
        target_id: Optional[int],
    ) -> bool:
        """
        Har bir tirik o'yinchi faqat 1 ta ovoz beradi.

        target_id=None -> Ovoz bermaslik.
        Hech qanday rol ovoz kuchini o'zgartirmaydi.
        """
        voter = self.players.get(voter_id)

        if voter is None:
            return False

        if not voter.alive or not voter.joined:
            return False

        if voter.voted:
            return False

        if target_id is not None:
            target = self.players.get(target_id)

            if target is None:
                return False

            if not target.alive or not target.joined:
                return False

        self.votes[voter_id] = target_id if target_id is not None else 0
        voter.voted = True

        return True

    def vote_counts(self) -> dict[int, int]:
        counts: dict[int, int] = {}

        for target_id in self.votes.values():
            if target_id == 0:
                continue

            counts[target_id] = counts.get(target_id, 0) + 1

        return counts

    def voting_result(self) -> Optional[int]:
        """
        Eng ko'p ovoz olgan tirik o'yinchini qaytaradi.

        Agar durang bo'lsa -> None.
        Agar ovoz berilmasa -> None.
        """
        counts = self.vote_counts()

        if not counts:
            return None

        highest = max(counts.values())

        leaders = [
            player_id
            for player_id, count in counts.items()
            if count == highest
        ]

        if len(leaders) != 1:
            return None

        target_id = leaders[0]

        target = self.players.get(target_id)

        if target is None or not target.alive:
            return None

        return target_id

    def clear_night_actions(self) -> None:
        self.night_actions.clear()

    def set_night_action(
        self,
        user_id: int,
        action: dict,
    ) -> bool:
        player = self.players.get(user_id)

        if player is None or not player.alive:
            return False

        self.night_actions[user_id] = action
        return True

    def get_night_action(self, user_id: int) -> Optional[dict]:
        return self.night_actions.get(user_id)

    def next_day(self) -> None:
        self.day_number += 1
        self.phase = GamePhase.DAY
        self.reset_votes()
        self.clear_night_actions()

    def start_night(self) -> None:
        self.phase = GamePhase.NIGHT
        self.clear_night_actions()

    def start_voting(self) -> None:
        self.phase = GamePhase.VOTING
        self.reset_votes()

    def start_game(self) -> bool:
        if self.started:
            return False

        if self.player_count() < 4:
            return False

        self.started = True
        self.ended = False
        self.phase = GamePhase.NIGHT
        self.day_number = 0

        return True

    def end_game(self, winner: str) -> None:
        self.phase = GamePhase.ENDED
        self.ended = True
        self.winner = winner

    def is_active(self) -> bool:
        return self.started and not self.ended

    def all_alive_players_voted(self) -> bool:
        alive = self.alive_players()

        if not alive:
            return False

        return all(player.voted for player in alive)
