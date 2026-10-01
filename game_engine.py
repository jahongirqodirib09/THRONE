from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from game_resolver import GameResolver, ResolutionResult
from game_state import GamePhase, GameState, PlayerState
from game_victory import VictoryEngine
from roles import get_role


@dataclass
class StartResult:
    success: bool
    message: str
    game: Optional[GameState] = None


@dataclass
class PhaseResult:
    success: bool
    message: str
    game: Optional[GameState] = None
    resolution: Optional[ResolutionResult] = None


class GameEngine:
    def __init__(self) -> None:
        self.games: dict[int, GameState] = {}
        self.resolver = GameResolver()
        self.victory = VictoryEngine()

    def create_game(self, group_id: int) -> GameState:
        existing = self.games.get(group_id)

        if existing is not None and existing.is_active():
            return existing

        game = GameState(group_id=group_id)
        self.games[group_id] = game

        return game

    def get_game(self, group_id: int) -> Optional[GameState]:
        return self.games.get(group_id)

    def has_active_game(self, group_id: int) -> bool:
        game = self.games.get(group_id)
        return game is not None and game.is_active()

    def add_player(
        self,
        group_id: int,
        user_id: int,
        name: str,
        username: Optional[str] = None,
    ) -> bool:
        game = self.games.get(group_id)

        if game is None:
            game = self.create_game(group_id)

        return game.add_player(
            user_id=user_id,
            name=name,
            username=username,
        )

    def remove_player(
        self,
        group_id: int,
        user_id: int,
    ) -> bool:
        game = self.games.get(group_id)

        if game is None:
            return False

        return game.remove_player(user_id)

    def can_start(self, group_id: int) -> tuple[bool, str]:
        game = self.games.get(group_id)

        if game is None:
            return False, "❌ Hali o‘yin yaratilmagan."

        if game.started:
            return False, "❌ O‘yin allaqachon boshlangan."

        count = game.player_count()

        if count < 4:
            return (
                False,
                f"❌ O‘yinni boshlash uchun kamida 4 o‘yinchi kerak. "
                f"Hozir: {count}",
            )

        return True, "✅ O‘yinni boshlash mumkin."

    def start_game(self, group_id: int) -> StartResult:
        game = self.games.get(group_id)

        if game is None:
            return StartResult(
                success=False,
                message="❌ Hali o‘yin yaratilmagan.",
            )

        can_start, reason = self.can_start(group_id)

        if not can_start:
            return StartResult(
                success=False,
                message=reason,
                game=game,
            )

        if not game.start_game():
            return StartResult(
                success=False,
                message="❌ O‘yinni boshlashning iloji bo‘lmadi.",
                game=game,
            )

        self._assign_roles(game)

        game.day_number = 1
        game.phase = GamePhase.NIGHT

        return StartResult(
            success=True,
            message="👑 THRONE o‘yini boshlandi.",
            game=game,
        )

    def _assign_roles(self, game: GameState) -> None:
        players = [
            player
            for player in game.players.values()
            if player.joined
        ]

        role_keys = self._build_role_pool(len(players))

        for player, role_key in zip(players, role_keys):
            role = get_role(role_key)

            if role is None:
                player.role = None
                player.side = None
                continue

            player.role = role.key
            player.side = role.side.value

    def _build_role_pool(self, player_count: int) -> list[str]:
        core_roles = [
            "shoh",
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

            "ovchi",
            "telba",
            "sayyoh",
            "yollanma_jangchi",
            "surgun_shahzoda",
            "taxt_da_vogari",
            "qaroqi",

            "sehrgar",
            "tabib",
            "kuzatuvchi",
            "qorovul",
            "solnomachi",
            "savdogar",
            "suiqasddchi",
        ]

        valid_roles = [
            key
            for key in core_roles
            if get_role(key) is not None
        ]

        if player_count <= len(valid_roles):
            return valid_roles[:player_count]

        extra_count = player_count - len(valid_roles)

        return valid_roles + ["qishloq_aholisi"] * extra_count

    def start_night(self, group_id: int) -> PhaseResult:
        game = self.games.get(group_id)

        if game is None:
            return PhaseResult(
                success=False,
                message="❌ O‘yin topilmadi.",
            )

        if not game.started or game.ended:
            return PhaseResult(
                success=False,
                message="❌ O‘yin faol emas.",
                game=game,
            )

        game.start_night()

        return PhaseResult(
            success=True,
            message="🌙 Tun boshlandi.",
            game=game,
        )

    def register_night_action(
        self,
        group_id: int,
        user_id: int,
        action: dict,
    ) -> bool:
        game = self.games.get(group_id)

        if game is None:
            return False

        if game.phase != GamePhase.NIGHT:
            return False

        player = game.get_player(user_id)

        if player is None:
            return False

        if not player.joined or not player.alive:
            return False

        return game.set_night_action(
            user_id,
            action,
        )

    def resolve_night(self, group_id: int) -> PhaseResult:
        game = self.games.get(group_id)

        if game is None:
            return PhaseResult(
                success=False,
                message="❌ O‘yin topilmadi.",
            )

        if game.phase != GamePhase.NIGHT:
            return PhaseResult(
                success=False,
                message="❌ Hozir tun bosqichi emas.",
                game=game,
            )

        resolution = self.resolver.resolve_night(game)

        victory = self.victory.check(game)

        if victory.game_ended:
            game.end_game(
                victory.main_winner or "Noma’lum"
            )

            return PhaseResult(
                success=True,
                message=victory.end_message,
                game=game,
                resolution=resolution,
            )

        game.next_day()

        return PhaseResult(
            success=True,
            message="☀️ Tun yakunlandi. Kun boshlandi.",
            game=game,
            resolution=resolution,
        )

    def start_day(self, group_id: int) -> PhaseResult:
        game = self.games.get(group_id)

        if game is None:
            return PhaseResult(
                success=False,
                message="❌ O‘yin topilmadi.",
            )

        if not game.started or game.ended:
            return PhaseResult(
                success=False,
                message="❌ O‘yin faol emas.",
                game=game,
            )

        game.phase = GamePhase.DAY

        return PhaseResult(
            success=True,
            message="☀️ Kun boshlandi.",
            game=game,
        )

    def start_voting(self, group_id: int) -> PhaseResult:
        game = self.games.get(group_id)

        if game is None:
            return PhaseResult(
                success=False,
                message="❌ O‘yin topilmadi.",
            )

        if game.phase != GamePhase.DAY:
            return PhaseResult(
                success=False,
                message=(
                    "❌ Ovoz berishni faqat kunduzgi "
                    "bosqichda boshlash mumkin."
                ),
                game=game,
            )

        game.start_voting()

        return PhaseResult(
            success=True,
            message="🗳️ Ovoz berish boshlandi.",
            game=game,
        )

    def register_vote(
        self,
        group_id: int,
        voter_id: int,
        target_id: Optional[int],
    ) -> bool:
        game = self.games.get(group_id)

        if game is None:
            return False

        if game.phase != GamePhase.VOTING:
            return False

        return game.register_vote(
            voter_id,
            target_id,
        )

    def resolve_voting(self, group_id: int) -> PhaseResult:
        game = self.games.get(group_id)

        if game is None:
            return PhaseResult(
                success=False,
                message="❌ O‘yin topilmadi.",
            )

        if game.phase != GamePhase.VOTING:
            return PhaseResult(
                success=False,
                message="❌ Hozir ovoz berish bosqichi emas.",
                game=game,
            )

        target_id = game.voting_result()

        message = (
            "⚖️ Durang yoki ovoz berilmagani sababli "
            "hech kim chiqarilmadi."
        )

        if target_id is not None:
            target = game.get_player(target_id)

            if target is not None and target.alive:
                votes = game.vote_counts().get(
                    target_id,
                    0,
                )

                target.alive = False
                target.voted = False

                message = (
                    f"☠️ <b>{target.name}</b> ovoz berish orqali "
                    f"o‘yindan chiqarildi.\n"
                    f"🗳️ Ovozlar: <b>{votes}</b>"
                )

        victory = self.victory.check(game)

        if victory.game_ended:
            game.end_game(
                victory.main_winner or "Noma’lum"
            )

            return PhaseResult(
                success=True,
                message=victory.end_message,
                game=game,
            )

        game.next_day()

        return PhaseResult(
            success=True,
            message=message,
            game=game,
        )

    def check_winner(self, group_id: int):
        game = self.games.get(group_id)

        if game is None:
            return None

        return self.victory.check(game)

    def alive_players(
        self,
        group_id: int,
    ) -> list[PlayerState]:
        game = self.games.get(group_id)

        if game is None:
            return []

        return game.alive_players()

    def end_game(
        self,
        group_id: int,
        winner: str,
    ) -> bool:
        game = self.games.get(group_id)

        if game is None:
            return False

        game.end_game(winner)
        return True

    def delete_game(self, group_id: int) -> bool:
        if group_id not in self.games:
            return False

        del self.games[group_id]

        return True

    def game_summary(
        self,
        group_id: int,
    ) -> Optional[dict]:
        game = self.games.get(group_id)

        if game is None:
            return None

        return {
            "group_id": game.group_id,
            "phase": game.phase.value,
            "day_number": game.day_number,
            "players": game.player_count(),
            "alive": game.alive_count(),
            "started": game.started,
            "ended": game.ended,
            "winner": game.winner,
    }
