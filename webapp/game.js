"use strict";

/*
============================================================
THRONE — MINI APP GAME
============================================================
Guruhdagi THRONE o'yinining Mini App ko'rinishi.

Bu qatlam:
- o'yin holatini oladi
- kun/tun holatini ko'rsatadi
- o'yinchilarni ko'rsatadi
- ovoz berish oynasini tayyorlaydi
- kuzatuvchi rejimini ko'rsatadi
- o'yin tugaganda natijani ko'rsatadi

Yashirin rol va maxfiy harakatlar boshqa o'yinchilarga
ochiq ko'rsatilmaydi.
============================================================
*/


const THRONE_GAME = {

    /* =====================================================
       STATE
    ===================================================== */

    state: {
        active: false,
        phase: "lobby",

        gameId: null,

        players: [],

        alivePlayers: [],

        eliminatedPlayers: [],

        currentPlayerId: null,

        myRole: null,
        mySide: null,

        nightAction: null,
        selectedTarget: null,

        votes: {},

        winner: null,

        lastUpdate: 0,

        polling: false,
        pollTimer: null
    },


    /* =====================================================
       CONFIG
    ===================================================== */

    config: {
        pollInterval: 5000,
        maxPlayersVisible: 35
    },


    /* =====================================================
       INIT
    ===================================================== */

    init() {

        if (
            typeof window === "undefined"
        ) {
            return;
        }

        this.bindEvents();

        this.createGameContainer();

        this.loadGame();

    },


    /* =====================================================
       CREATE CONTAINER
    ===================================================== */

    createGameContainer() {

        let container =
            document.querySelector(
                "#throne-game"
            );

        if (container) {
            return container;
        }


        const main =
            document.querySelector(
                "main"
            ) ||
            document.body;


        container =
            document.createElement(
                "section"
            );


        container.id =
            "throne-game";


        container.style.display =
            "none";


        container.innerHTML = `
            <div
                class="throne-game-header"
                style="
                    display:flex;
                    align-items:center;
                    justify-content:space-between;
                    gap:10px;
                    margin-bottom:14px;
                "
            >

                <div>
                    <div
                        style="
                            font-size:10px;
                            letter-spacing:2px;
                            color:#a9a49a;
                        "
                    >
                        THRONE
                    </div>

                    <div
                        id="throne-game-title"
                        style="
                            font-size:20px;
                            font-weight:800;
                            margin-top:3px;
                        "
                    >
                        Qirollik o‘yini
                    </div>
                </div>

                <div
                    id="throne-game-phase"
                    style="
                        padding:7px 10px;
                        border-radius:10px;
                        background:#111;
                        border:1px solid rgba(255,255,255,.08);
                        font-size:10px;
                        font-weight:700;
                    "
                >
                    LOBBY
                </div>

            </div>


            <div
                id="throne-game-status"
                style="
                    margin-bottom:14px;
                "
            ></div>


            <div
                id="throne-game-players"
                style="
                    display:grid;
                    grid-template-columns:
                        repeat(
                            auto-fit,
                            minmax(120px,1fr)
                        );
                    gap:8px;
                "
            ></div>


            <div
                id="throne-game-actions"
                style="
                    margin-top:14px;
                "
            ></div>


            <div
                id="throne-game-result"
                style="
                    margin-top:14px;
                "
            ></div>

        `;


        main.appendChild(
            container
        );


        return container;
    },


    /* =====================================================
       LOAD GAME
    ===================================================== */

    async loadGame() {

        try {

            if (
                typeof THRONE_API ===
                "undefined"
            ) {
                return;
            }


            const response =
                await THRONE_API.getGameState();


            if (
                !response ||
                response.demo
            ) {

                this.renderDemo();

                return;
            }


            this.applyGameData(
                response
            );


            this.render();


        } catch (error) {

            console.error(
                "THRONE game load error:",
                error
            );

            this.renderError(
                "O‘yin ma’lumotlarini yuklashda xatolik."
            );
        }
    },


    /* =====================================================
       APPLY DATA
    ===================================================== */

    applyGameData(data) {

        const game =
            data.data ||
            data.game ||
            data;


        if (!game) {
            return;
        }


        this.state.active =
            Boolean(
                game.active ??
                game.running ??
                false
            );


        this.state.gameId =
            game.game_id ??
            game.id ??
            null;


        this.state.phase =
            game.phase ??
            game.status ??
            "lobby";


        this.state.players =
            Array.isArray(
                game.players
            )
                ? game.players
                : [];


        this.state.alivePlayers =
            Array.isArray(
                game.alive_players
            )
                ? game.alive_players
                : this.state.players.filter(
                    player =>
                        player.alive !== false
                );


        this.state.eliminatedPlayers =
            Array.isArray(
                game.eliminated_players
            )
                ? game.eliminated_players
                : this.state.players.filter(
                    player =>
                        player.alive === false
                );


        this.state.currentPlayerId =
            game.current_player_id ??
            null;


        /*
        Hidden role faqat o'zimizga tegishli
        backend javobida mavjud bo'lsa olinadi.
        */

        this.state.myRole =
            game.my_role ??
            null;


        this.state.mySide =
            game.my_side ??
            null;


        this.state.nightAction =
            game.night_action ??
            null;


        this.state.winner =
            game.winner ??
            null;


        this.state.lastUpdate =
            Date.now();
    },


    /* =====================================================
       DEMO
    ===================================================== */

    renderDemo() {

        this.state.active =
            true;

        this.state.phase =
            "lobby";

        this.state.gameId =
            "demo";

        this.state.players = [
            {
                id: 1,
                name: "Shoh",
                alive: true
            },
            {
                id: 2,
                name: "Malika",
                alive: true
            },
            {
                id: 3,
                name: "Vazir",
                alive: true
            },
            {
                id: 4,
                name: "Qo‘mondon",
                alive: true
            }
        ];


        this.state.alivePlayers =
            this.state.players;


        this.render();
    },


    /* =====================================================
       RENDER
    ===================================================== */

    render() {

        const container =
            document.querySelector(
                "#throne-game"
            );


        if (!container) {
            return;
        }


        container.style.display =
            "block";


        this.renderPhase();

        this.renderStatus();

        this.renderPlayers();

        this.renderActions();

        this.renderResult();
    },


    /* =====================================================
       PHASE
    ===================================================== */

    renderPhase() {

        const phase =
            document.querySelector(
                "#throne-game-phase"
            );


        if (!phase) {
            return;
        }


        const phaseData =
            this.getPhaseData(
                this.state.phase
            );


        phase.textContent =
            phaseData.label;


        phase.style.color =
            phaseData.color;
    },


    /* =====================================================
       PHASE DATA
    ===================================================== */

    getPhaseData(phase) {

        const phases = {

            lobby: {
                label: "LOBBY",
                color: "#d4af37"
            },

            role_reveal: {
                label: "ROL",
                color: "#d4af37"
            },

            night: {
                label: "🌙 TUN",
                color: "#9c9cff"
            },

            day: {
                label: "☀️ KUN",
                color: "#e7c766"
            },

            discussion: {
                label: "💬 MUHOKAMA",
                color: "#d4af37"
            },

            voting: {
                label: "🗳️ OVOZ",
                color: "#e6b95c"
            },

            last_words: {
                label: "🕯️ SO‘NGGI SO‘Z",
                color: "#c9c1b4"
            },

            finished: {
                label: "👑 YAKUN",
                color: "#d4af37"
            },

            stopped: {
                label: "⛔ TO‘XTATILDI",
                color: "#9d9a91"
            }
        };


        return (
            phases[phase] ||
            {
                label: String(
                    phase || "O‘YIN"
                ).toUpperCase(),

                color: "#d4af37"
            }
        );
    },


    /* =====================================================
       STATUS
    ===================================================== */

    renderStatus() {

        const element =
            document.querySelector(
                "#throne-game-status"
            );


        if (!element) {
            return;
        }


        const alive =
            this.state.alivePlayers.length;


        const total =
            this.state.players.length;


        const phase =
            this.getPhaseData(
                this.state.phase
            );


        element.innerHTML = `
            <div
                style="
                    padding:14px;
                    border-radius:15px;
                    background:#0c0c0c;
                    border:1px solid rgba(255,255,255,.07);
                "
            >

                <div
                    style="
                        font-size:10px;
                        color:#9d9a91;
                        letter-spacing:1px;
                    "
                >
                    JORIY HOLAT
                </div>

                <div
                    style="
                        margin-top:7px;
                        font-size:13px;
                        font-weight:700;
                    "
                >
                    ${this.escape(
                        this.getPhaseDescription(
                            this.state.phase
                        )
                    )}
                </div>

                <div
                    style="
                        display:flex;
                        gap:8px;
                        flex-wrap:wrap;
                        margin-top:10px;
                    "
                >

                    <span
                        style="
                            padding:5px 8px;
                            border-radius:8px;
                            background:#151515;
                            color:#c9c1b4;
                            font-size:9px;
                        "
                    >
                        👥 ${total} o‘yinchi
                    </span>

                    <span
                        style="
                            padding:5px 8px;
                            border-radius:8px;
                            background:#151515;
                            color:#c9c1b4;
                            font-size:9px;
                        "
                    >
                        ❤️ ${alive} tirik
                    </span>

                    <span
                        style="
                            padding:5px 8px;
                            border-radius:8px;
                            background:#151515;
                            color:${phase.color};
                            font-size:9px;
                        "
                    >
                        ${phase.label}
                    </span>

                </div>

            </div>
        `;
    },


    /* =====================================================
       PHASE DESCRIPTION
    ===================================================== */

    getPhaseDescription(phase) {

        const descriptions = {

            lobby:
                "O‘yinchilar qirollikka qo‘shilmoqda.",

            role_reveal:
                "Har bir o‘yinchiga yashirin vazifasi berilmoqda.",

            night:
                "Qirollik tun bag‘rida. Maxfiy harakatlar bajarilmoqda.",

            day:
                "Tong otdi. Kechagi voqealar e’lon qilinmoqda.",

            discussion:
                "O‘yinchilar vaziyatni muhokama qilmoqda.",

            voting:
                "Ovoz berish boshlandi.",

            last_words:
                "Eliminatsiya qilingan o‘yinchiga so‘nggi so‘z berildi.",

            finished:
                "O‘yin yakunlandi.",

            stopped:
                "O‘yin administrator tomonidan to‘xtatildi."
        };


        return (
            descriptions[phase] ||
            "THRONE o‘yini davom etmoqda."
        );
    },


    /* =====================================================
       PLAYERS
    ===================================================== */

    renderPlayers() {

        const container =
            document.querySelector(
                "#throne-game-players"
            );


        if (!container) {
            return;
        }


        const players =
            this.state.players
                .slice(
                    0,
                    this.config.maxPlayersVisible
                );


        if (!players.length) {

            container.innerHTML = `
                <div
                    style="
                        grid-column:1/-1;
                        padding:22px;
                        text-align:center;
                        color:#9d9a91;
                    "
                >
                    Hozircha o‘yinchi yo‘q.
                </div>
            `;

            return;
        }


        container.innerHTML =
            players
                .map(
                    player =>
                        this.playerCard(
                            player
                        )
                )
                .join("");
    },


    /* =====================================================
       PLAYER CARD
    ===================================================== */

    playerCard(player) {

        const alive =
            player.alive !== false;


        const isCurrent =
            String(
                player.id
            ) ===
            String(
                this.state.currentPlayerId
            );


        const selected =
            String(
                player.id
            ) ===
            String(
                this.state.selectedTarget
            );


        let border =
            "rgba(255,255,255,.07)";


        if (selected) {
            border =
                "rgba(212,175,55,.7)";
        }


        return `
            <button
                type="button"
                class="throne-player-card"
                data-player-id="${this.escapeAttr(
                    player.id
                )}"
                style="
                    text-align:left;
                    border:1px solid ${border};
                    background:${alive
                        ? "#0d0d0d"
                        : "#090909"};
                    border-radius:13px;
                    padding:12px;
                    color:#fff;
                    opacity:${alive ? "1" : ".48"};
                    cursor:${alive
                        ? "pointer"
                        : "default"};
                "
            >

                <div
                    style="
                        display:flex;
                        align-items:center;
                        gap:9px;
                    "
                >

                    <div
                        style="
                            width:34px;
                            height:34px;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            border-radius:50%;
                            background:#171717;
                            border:1px solid rgba(212,175,55,.18);
                            font-size:17px;
                        "
                    >
                        ${alive ? "♟️" : "💀"}
                    </div>

                    <div
                        style="
                            min-width:0;
                            flex:1;
                        "
                    >

                        <div
                            style="
                                font-size:11px;
                                font-weight:700;
                                overflow:hidden;
                                text-overflow:ellipsis;
                                white-space:nowrap;
                            "
                        >
                            ${this.escape(
                                player.name ||
                                "Noma’lum"
                            )}
                        </div>

                        <div
                            style="
                                margin-top:3px;
                                font-size:8px;
                                color:#8f8b82;
                            "
                        >
                            ${alive
                                ? (
                                    isCurrent
                                        ? "SIZ"
                                        : "TIRIK"
  
