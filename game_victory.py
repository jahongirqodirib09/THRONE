from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from game_state import GameState, PlayerState
from roles import Side, get_role


@dataclass
class Winner:
    user_id: Optional[int]
    name: str
    role: Optional[str]
    side: str
    reason: str


@dataclass
class VictoryResult:
    game_ended: bool = False
    main_winner: Optional[str] = None

    winners: list[Winner] = field(default_factory=list)
    losers: list[PlayerState] = field(default_factory=list)

    message: str = ""


class VictoryEngine:
    """
    THRONE g'alaba tizimi.

    Asosiy tomonlar:
        TAHT
        SOYA
        YAKKA
        MAXSUS

    Muhim:
    - Oddiy ovoz g'alabasi alohida hisoblanadi.
    - Yakka rollar shaxsiy shartlari bilan g'alaba qozonishi mumkin.
    - Maxsus rollar o'zlarining maxsus shartlariga ega bo'lishi mumkin.
    """

    # =========================================================
    # ASOSIY TEKSHIRUV
    # =========================================================

    def check(
        self,
        game: GameState,
    ) -> VictoryResult:

        if game.ended:
            return VictoryResult(
                game_ended=True,
                main_winner=game.winner,
                message="O'yin allaqachon yakunlangan.",
            )

        alive = game.alive_players()

        if not alive:
            return self._no_alive_players(game)

        throne = [
            player
            for player in alive
            if self._player_side(player) == Side.THRONE
        ]

        shadow = [
            player
            for player in alive
            if self._player_side(player) == Side.SHADOW
        ]

        solo = [
            player
            for player in alive
            if self._player_side(player) == Side.SOLO
        ]

        special = [
            player
            for player in alive
            if self._player_side(player) == Side.SPECIAL
        ]

        # -----------------------------------------------------
        # YAKKA MAXSUS G'ALABALARI
        # -----------------------------------------------------

        individual_winners = self._check_individual_winners(
            game
        )

        # Individual g'alaba o'yinni avtomatik tugatmaydi.
        # Chunki boshqa tomonlar ham o'z shartlarini bajarishi mumkin.

        # -----------------------------------------------------
        # TAHT / SOYA
        # -----------------------------------------------------

        main_winner = self._check_main_sides(
            throne_count=len(throne),
            shadow_count=len(shadow),
            solo_count=len(solo),
            special_count=len(special),
        )

        if main_winner is None:
            return VictoryResult(
                game_ended=False,
                winners=individual_winners,
                message="O'yin davom etmoqda.",
            )

        all_winners = list(individual_winners)

        all_winners.extend(
            self._side_winners(
                game,
                main_winner,
            )
        )

        game.end_game(main_winner)

        losers = [
            player
            for player in game.players.values()
            if player.joined
            and player not in [
                winner_player
                for winner_player in []
            ]
        ]

        result = VictoryResult(
            game_ended=True,
            main_winner=main_winner,
            winners=all_winners,
            losers=losers,
            message=self._build_end_message(
                game,
                main_winner,
                all_winners,
            ),
        )

        return result

    # =========================================================
    # TAHT / SOYA
    # =========================================================

    def _check_main_sides(
        self,
        throne_count: int,
        shadow_count: int,
        solo_count: int,
        special_count: int,
    ) -> Optional[str]:

        # -----------------------------------------------------
        # SOYA YO'Q
        # -----------------------------------------------------

        if shadow_count == 0 and throne_count > 0:
            return "TAHT"

        # -----------------------------------------------------
        # TAHT YO'Q
        # -----------------------------------------------------

        if throne_count == 0 and shadow_count > 0:
            return "SOYA"

        # -----------------------------------------------------
        # SOYA SON JIHATDAN USTUN
        # -----------------------------------------------------

        if (
            throne_count > 0
            and shadow_count > 0
            and shadow_count >= throne_count
            and solo_count == 0
            and special_count == 0
        ):
            return "SOYA"

        return None

    # =========================================================
    # O'YINCHINING TOMONINI ANIQLASH
    # =========================================================

    def _player_side(
        self,
        player: PlayerState,
    ) -> Optional[Side]:

        if player.role is None:
            return None

        role = get_role(player.role)

        if role is None:
            return None

        return role.side

    # =========================================================
    # TOMON G'OLIBI
    # =========================================================

    def _side_winners(
        self,
        game: GameState,
        side_name: str,
    ) -> list[Winner]:

        winners: list[Winner] = []

        for player in game.alive_players():

            role = get_role(player.role)

            if role is None:
                continue

            if side_name == "TAHT":
                if role.side != Side.THRONE:
                    continue

                winners.append(
                    Winner(
                        user_id=player.user_id,
                        name=player.name,
                        role=role.name,
                        side="TAHT",
                        reason="Taxt tomoni g'alaba qozondi.",
                    )
                )

            elif side_name == "SOYA":
                if role.side != Side.SHADOW:
                    continue

                winners.append(
                    Winner(
                        user_id=player.user_id,
                        name=player.name,
                        role=role.name,
                        side="SOYA",
                        reason="Soya tomoni g'alaba qozondi.",
                    )
                )

        return winners

    # =========================================================
    # YAKKA / SHAXSIY G'ALABALAR
    # =========================================================

    def _check_individual_winners(
        self,
        game: GameState,
    ) -> list[Winner]:

        winners: list[Winner] = []

        for player in game.players.values():

            if not player.joined:
                continue

            role = get_role(player.role)

            if role is None:
                continue

            # -------------------------------------------------
            # TELBA
            # -------------------------------------------------

            if role.key == "telba":

                # Telbaning asosiy maqsadi:
                # kunduzgi ovoz bilan chiqarilish.
                #
                # Bu holat resolve_voting() tomonidan
                # player.alive = False qilinganda qayd qilinadi.
                #
                # Hozir tirik Telba g'olib bo'lmaydi.
                continue

            # -------------------------------------------------
            # OVCHI
            # -------------------------------------------------

            if role.key == "ovchi":

                if self._hunter_condition(game, player):
                    winners.append(
                        Winner(
                            user_id=player.user_id,
                            name=player.name,
                            role=role.name,
                            side="YAKKA",
                            reason="Ovchi o'zining shaxsiy maqsadini bajardi.",
                        )
                    )

            # -------------------------------------------------
            # SAYYOH
            # -------------------------------------------------

            elif role.key == "sayyoh":

                if self._is_last_stage_survivor(game, player):
                    winners.append(
                        Winner(
                            user_id=player.user_id,
                            name=player.name,
                            role=role.name,
                            side="YAKKA",
                            reason="Sayyoh o'yin oxirigacha omon qoldi.",
                        )
                    )

            # -------------------------------------------------
            # YOLLANMA JANGCHI
            # -------------------------------------------------

            elif role.key == "yollanma_jangchi":

                if self._mercenary_condition(game, player):
                    winners.append(
                        Winner(
                            user_id=player.user_id,
                            name=player.name,
                            role=role.name,
                            side="YAKKA",
                            reason="Yollanma jangchi shaxsiy shartini bajardi.",
                        )
                    )

            # -------------------------------------------------
            # SURGUN SHAHZODA
            # -------------------------------------------------

            elif role.key == "surgun_shahzoda":

                if self._exiled_prince_condition(
                    game,
                    player,
                ):
                    winners.append(
                        Winner(
                            user_id=player.user_id,
                            name=player.name,
                            role=role.name,
                            side="YAKKA",
                            reason="Surgun shahzoda o'z maqsadiga erishdi.",
                        )
                    )

            # -------------------------------------------------
            # TAHT DA'VOGARI
            # -------------------------------------------------

            elif role.key == "taxt_davogari":

                if self._throne_claimant_condition(
                    game,
                    player,
                ):
                    winners.append(
                        Winner(
                            user_id=player.user_id,
                            name=player.name,
                            role=role.name,
                            side="YAKKA",
                            reason="Taxt da'vogari shaxsiy taxt shartini bajardi.",
                        )
                    )

            # -------------------------------------------------
            # QAROQI
            # -------------------------------------------------

            elif role.key == "qaroqi":

                if self._thief_condition(game, player):
                    winners.append(
                        Winner(
                            user_id=player.user_id,
                            name=player.name,
                            role=role.name,
                            side="YAKKA",
                            reason="Qaroqi boylik bo'yicha shaxsiy maqsadini bajardi.",
                        )
                    )

            # -------------------------------------------------
            # MAXSUS SUIQASDCHI
            # -------------------------------------------------

            elif role.key == "suiqasddchi":

                if self._assassin_condition(game, player):
                    winners.append(
                        Winner(
                            user_id=player.user_id,
                            name=player.name,
                            role=role.name,
                            side="MAXSUS",
                            reason="Suiqasdchi shaxsiy nishon shartini bajardi.",
                        )
                    )

        return winners

    # =========================================================
    # OVCHI SHARTI
    # =========================================================

    def _hunter_condition(
        self,
        game: GameState,
        player: PlayerState,
    ) -> bool:

        # Keyingi bosqichda ovchining statistikasi orqali
        # aniq 2 ta hujum sharti ulanadi.
        #
        # Hozircha u tirik qolgan bo'lsa,
        # avtomatik g'alaba berilmaydi.

        return False

    # =========================================================
    # SAYYOH SHARTI
    # =========================================================

    def _is_last_stage_survivor(
        self,
        game: GameState,
        player: PlayerState,
    ) -> bool:

        if not player.alive:
            return False

        alive = game.alive_players()

        if len(alive) != 1:
            return False

        return alive[0].user_id == player.user_id

    # =========================================================
    # YOLLANMA JANGCHI
    # =========================================================

    def _mercenary_condition(
        self,
        game: GameState,
        player: PlayerState,
    ) -> bool:

        return False

    # =========================================================
    # SURGUN SHAHZODA
    # =========================================================

    def _exiled_prince_condition(
        self,
        game: GameState,
        player: PlayerState,
    ) -> bool:

        return False

    # =========================================================
    # TAHT DA'VOGARI
    # =========================================================

    def _throne_claimant_condition(
        self,
        game: GameState,
        player: PlayerState,
    ) -> bool:

        return False

    # =========================================================
    # QAROQI
    # =========================================================

    def _thief_condition(
        self,
        game: GameState,
        player: PlayerState,
    ) -> bool:

        return False

    # =========================================================
    # SUIQASDCHI
    # =========================================================

    def _assassin_condition(
        self,
        game: GameState,
        player: PlayerState,
    ) -> bool:

        return False

    # =========================================================
    # HECH KIM TIRIK QOLMAGANDA
    # =========================================================

    def _no_alive_players(
        self,
        game: GameState,
    ) -> VictoryResult:

        game.end_game("hech kim")

        return VictoryResult(
            game_ended=True,
            main_winner="hech kim",
            message=(
                "☠️ O'yinda tirik o'yinchi qolmadi."
            ),
        )

    # =========================================================
    # YAKUNIY XABAR
    # =========================================================

    def _build_end_message(
        self,
        game: GameState,
        main_winner: str,
        winners: list[Winner],
    ) -> str:

        lines = [
            "👑⚔️ THRONE — O'YIN YAKUNLANDI",
            "",
            f"🏆 G'olib tomon: {main_winner}",
        ]

        if winners:
            lines.append("")
            lines.append("🎖️ G'oliblar:")

            shown_ids: set[int] = set()

            for winner in winners:

                if winner.user_id is not None:
                    if winner.user_id in shown_ids:
                        continue

                    shown_ids.add(
                        winner.user_id
                    )

                lines.append(
                    f"• {winner.name} — {winner.role}"
                )

        return "\n".join(lines)
