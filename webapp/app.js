"use strict";

/*
============================================================
THRONE — MINI APP
============================================================
Frontend foundation.

Backend API keyinchalik shu fayldagi loadPlayerData()
funksiyasiga ulanadi.
============================================================
*/


/* =========================================================
   GLOBAL STATE
========================================================= */

const state = {
    user: {
        id: null,
        username: "",
        firstName: "THRONE Player",
        lastName: "",
    },

    player: {
        name: "THRONE PLAYER",
        level: 1,
        xp: 0,
        xpMax: 100,

        gold: 0,
        coin: 0,
        diamond: 0,

        elite: true,

        castleLevel: 1,
        defense: 0,
        armyPower: 0,

        clan: "Yo‘q",
    },

    world: {
        mode: "day",
        lastChange: Date.now(),
    },

    currentPage: "home",

    initialized: false,
};


/* =========================================================
   DOM HELPERS
========================================================= */

function $(selector) {
    return document.querySelector(selector);
}


function $all(selector) {
    return Array.from(
        document.querySelectorAll(selector)
    );
}


/* =========================================================
   SAFE TEXT
========================================================= */

function setText(selector, value) {
    const element = $(selector);

    if (!element) {
        return;
    }

    element.textContent = value;
}


/* =========================================================
   NUMBER FORMAT
========================================================= */

function formatNumber(value) {
    if (value === "∞") {
        return "∞";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "0";
    }

    return number.toLocaleString("en-US");
}


/* =========================================================
   TELEGRAM MINI APP
========================================================= */

function getTelegramWebApp() {
    if (
        typeof window !== "undefined" &&
        window.Telegram &&
        window.Telegram.WebApp
    ) {
        return window.Telegram.WebApp;
    }

    return null;
}


function initTelegramWebApp() {
    const webApp = getTelegramWebApp();

    if (!webApp) {
        return null;
    }

    try {
        webApp.ready();

        if (typeof webApp.expand === "function") {
            webApp.expand();
        }

        if (
            typeof webApp.disableVerticalSwipes === "function"
        ) {
            webApp.disableVerticalSwipes();
        }

    } catch (error) {
        console.warn(
            "Telegram WebApp initialization error:",
            error
        );
    }

    return webApp;
}


/* =========================================================
   TELEGRAM USER
========================================================= */

function loadTelegramUser() {
    const webApp = getTelegramWebApp();

    if (!webApp) {
        return;
    }

    try {
        const user = webApp.initDataUnsafe?.user;

        if (!user) {
            return;
        }

        state.user.id = user.id || null;
        state.user.username = user.username || "";
        state.user.firstName =
            user.first_name || "THRONE Player";
        state.user.lastName =
            user.last_name || "";

        const fullName = [
            state.user.firstName,
            state.user.lastName,
        ]
            .filter(Boolean)
            .join(" ");

        if (fullName) {
            state.player.name = fullName;
        }

    } catch (error) {
        console.warn(
            "Telegram user data error:",
            error
        );
    }
}


/* =========================================================
   LOAD PLAYER DATA
========================================================= */

async function loadPlayerData() {

    /*
    ---------------------------------------------------------
    Hozircha local foundation.
    Keyinchalik backend API shu yerga ulanadi.
    ---------------------------------------------------------
    */

    const savedUserId = state.user.id;

    if (savedUserId) {
        state.player.name =
            [
                state.user.firstName,
                state.user.lastName,
            ]
                .filter(Boolean)
                .join(" ");
    }

    updatePlayerUI();
}


/* =========================================================
   UPDATE PLAYER UI
========================================================= */

function updatePlayerUI() {

    setText(
        "#player-name",
        state.player.name
    );

    setText(
        "#player-level",
        state.player.level
    );

    setText(
        "#xp-text",
        `${formatNumber(state.player.xp)} / ${formatNumber(state.player.xpMax)} XP`
    );


    /* -----------------------------------------------------
       XP
    ----------------------------------------------------- */

    const xpProgress = $("#xp-progress");

    if (xpProgress) {

        const xpMax =
            Math.max(1, Number(state.player.xpMax));

        const xp =
            Math.max(
                0,
                Math.min(
                    Number(state.player.xp),
                    xpMax
                )
            );

        const percent =
            (xp / xpMax) * 100;

        xpProgress.style.width =
            `${percent}%`;
    }


    /* -----------------------------------------------------
       Resources
    ----------------------------------------------------- */

    setText(
        "#gold-value",
        state.player.gold
    );

    setText(
        "#coin-value",
        state.player.coin
    );

    setText(
        "#diamond-value",
        state.player.diamond
    );

    setText(
        "#elite-value",
        state.player.elite
            ? "FAOL"
            : "FAOL EMAS"
    );


    /* -----------------------------------------------------
       Kingdom
    ----------------------------------------------------- */

    setText(
        "#castle-level",
        `${state.player.castleLevel}-daraja`
    );

    setText(
        "#defense-value",
        formatNumber(state.player.defense)
    );

    setText(
        "#army-power",
        formatNumber(state.player.armyPower)
    );

    setText(
        "#clan-name",
        state.player.clan || "Yo‘q"
    );
}


/* =========================================================
   WORLD MODE
========================================================= */

function setWorldMode(mode) {

    if (
        mode !== "day" &&
        mode !== "night"
    ) {
        mode = "day";
    }

    state.world.mode = mode;
    state.world.lastChange = Date.now();

    const scene =
        $("#kingdom-scene");

    const time =
        $("#world-time");

    if (scene) {

        scene.classList.remove(
            "day",
            "night"
        );

        scene.classList.add(mode);
    }

    if (time) {

        time.textContent =
            mode === "day"
                ? "DAY"
                : "NIGHT";
    }
}


/* =========================================================
   AUTOMATIC DAY / NIGHT
========================================================= */

function calculateWorldMode() {

    const hour =
        new Date().getHours();

    if (hour >= 6 && hour < 18) {
        return "day";
    }

    return "night";
}


function updateWorldMode() {

    setWorldMode(
        calculateWorldMode()
    );
}


/* =========================================================
   PAGE SYSTEM
========================================================= */

function setActiveNavigation(page) {

    $all(".nav-button").forEach(
        (button) => {

            const buttonPage =
                button.dataset.page;

            button.classList.toggle(
                "active",
                buttonPage === page
            );
        }
    );
}


function openPage(page) {

    if (!page) {
        return;
    }

    state.currentPage = page;

    setActiveNavigation(page);


    switch (page) {

        case "home":
            scrollToTop();
            break;

        case "kingdom":
            openKingdomPage();
            break;

        case "inventory":
            openInventoryPage();
            break;

        case "clan":
            openClanPage();
            break;

        case "profile":
            openProfilePage();
            break;

        case "game":
            openGamePage();
            break;

        default:
            scrollToTop();
            break;
    }
}


/* =========================================================
   SCROLL
========================================================= */

function scrollToTop() {

    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });
}


/* =========================================================
   MODAL
========================================================= */

function openModal(content) {

    const modal =
        $("#modal");

    const modalContent =
        $("#modal-content");

    if (!modal || !modalContent) {
        return;
    }

    modalContent.innerHTML =
        content;

    modal.classList.remove(
        "hidden"
    );
}


function closeModal() {

    const modal =
        $("#modal");

    if (!modal) {
        return;
    }

    modal.classList.add(
        "hidden"
    );
}


/* =========================================================
   PROFILE PAGE
========================================================= */

function openProfilePage() {

    openModal(`
        <div>
            <div class="section-label">
                PROFIL
            </div>

            <h2 style="margin-top:6px;">
                ${escapeHtml(state.player.name)}
            </h2>

            <div class="status-list" style="margin-top:16px;">

                <div class="status-item">
                    <span>⭐ Level</span>
                    <strong>${state.player.level}</strong>
                </div>

                <div class="status-item">
                    <span>✨ XP</span>
                    <strong>
                        ${formatNumber(state.player.xp)}
                    </strong>
                </div>

                <div class="status-item">
                    <span>🟡 Oltin</span>
                    <strong>
                        ${formatNumber(state.player.gold)}
                    </strong>
                </div>

                <div class="status-item">
                    <span>🪙 Coin</span>
                    <strong>
                        ${formatNumber(state.player.coin)}
                    </strong>
                </div>

                <div class="status-item">
                    <span>💎 Olmos</span>
                    <strong>
                        ${formatNumber(state.player.diamond)}
                    </strong>
                </div>

                <div class="status-item">
                    <span>⚜️ Elite</span>
                    <strong>
                        ${state.player.elite
                            ? "AKTIV"
                            : "FAOL EMAS"}
                    </strong>
                </div>

            </div>
        </div>
    `);
}


/* =========================================================
   KINGDOM PAGE
========================================================= */

function openKingdomPage() {

    openModal(`
        <div>
            <div class="section-label">
                QIROLLIK
            </div>

            <h2 style="margin-top:6px;">
                ${escapeHtml(state.player.name)} Qirolligi
            </h2>

            <div class="status-list" style="margin-top:16px;">

                <div class="status-item">
                    <span>🏰 Qal'a</span>
                    <strong>
                        ${state.player.castleLevel}-daraja
                    </strong>
                </div>

                <div class="status-item">
                    <span>🛡️ Mudofaa</span>
                    <strong>
                        ${formatNumber(state.player.defense)}
                    </strong>
                </div>

                <div class="status-item">
                    <span>⚔️ Harbiy kuch</span>
                    <strong>
                        ${formatNumber(state.player.armyPower)}
                    </strong>
                </div>

                <div class="status-item">
                    <span>🏴 Klan</span>
                    <strong>
                        ${escapeHtml(state.player.clan)}
                    </strong>
                </div>

            </div>

            <button
                type="button"
                class="primary-button"
                data-close-modal
            >
                👑 Qirollikka qaytish
            </button>
        </div>
    `);
}


/* =========================================================
   INVENTORY PAGE
========================================================= */

function openInventoryPage() {

    openModal(`
        <div>

            <div class="section-label">
                INVENTAR
            </div>

            <h2 style="margin-top:6px;">
                Jihozlar
            </h2>

            <div
                style="
                    margin-top:16px;
                    padding:18px;
                    border:1px solid rgba(255,255,255,.06);
                    border-radius:15px;
                    background:#0d0d0d;
                    text-align:center;
                "
            >
                <div style="font-size:38px;">
                    🎒
                </div>

                <div
                    style="
                        margin-top:10px;
                        font-weight:700;
                    "
                >
                    Inventar tayyor
                </div>

                <div
                    style="
                        margin-top:5px;
                        color:#9d9a91;
                        font-size:10px;
                    "
                >
                    Qurol, kiyim, ot va boshqa jihozlar
                    backend bilan ulanadi.
                </div>
            </div>

        </div>
    `);
}


/* =========================================================
   CLAN PAGE
========================================================= */

function openClanPage() {

    openModal(`
        <div>

            <div class="section-label">
                KLAN
            </div>

            <h2 style="margin-top:6px;">
                ${escapeHtml(state.player.clan)}
            </h2>

            <div
                style="
                    margin-top:16px;
                    padding:18px;
                    border:1px solid rgba(212,175,55,.12);
                    border-radius:15px;
                    background:#0d0d0d;
                "
            >

                <div style="font-size:34px;">
                    🏴
                </div>

                <div
                    style="
                        margin-top:10px;
                        font-size:12px;
                        font-weight:700;
                    "
                >
                    Klan tizimi
                </div>

                <div
                    style="
                        margin-top:5px;
                        color:#9d9a91;
                        font-size:10px;
                        line-height:1.5;
                    "
                >
                    Klanlar, a'zolar, urushlar va reytinglar
                    THRONE backend tizimi bilan ishlaydi.
                </div>

            </div>

        </div>
    `);
}


/* =========================================================
   GAME PAGE
========================================================= */

function openGamePage() {

    openModal(`
        <div>

            <div class="section-label">
                THRONE GAME
            </div>

            <h2 style="margin-top:6px;">
                ⚔️ Guruh o‘yini
            </h2>

            <div
                style="
                    margin-top:16px;
                    padding:18px;
                    border:1px solid rgba(212,175,55,.12);
                    border-radius:15px;
                    background:#0d0d0d;
                "
            >

                <div
                    style="
                        font-size:40px;
                        text-align:center;
                    "
                >
                    👑
                </div>

                <div
                    style="
                        margin-top:10px;
                        font-size:12px;
                        font-weight:700;
                        text-align:center;
                    "
                >
                    Qirollik taqdiri seni kutmoqda
                </div>

                <div
                    style="
                        margin-top:7px;
                        color:#9d9a91;
                        font-size:10px;
                        line-height:1.5;
                        text-align:center;
                    "
                >
                    O‘yin boshlanganida guruhdagi
                    real vaqt holati shu Mini App oynasida
                    ko‘rsatiladi.
                </div>

            </div>

            <button
                type="button"
                class="primary-button"
                data-close-modal
            >
                ⚔️ O‘yinga qaytish
            </button>

        </div>
    `);
}


/* =========================================================
   INVITE
========================================================= */

function inviteFriends() {

    const webApp =
        getTelegramWebApp();

    const botUsername =
        "Taxtlar_bot";

    const inviteText =
        "👑 THRONE qirolligiga qo‘shil!";

    const inviteUrl =
        `https://t.me/${botUsername}`;

    const shareUrl =
        `https://t.me/share/url?url=${encodeURIComponent(inviteUrl)}&text=${encodeURIComponent(inviteText)}`;

    if (webApp && typeof webApp.openTelegramLink === "function") {

        try {
            webApp.openTelegramLink(
                shareUrl
            );

            return;

        } catch (error) {
            console.warn(
                "Telegram share error:",
                error
            );
        }
    }

    if (
        typeof window !== "undefined" &&
        typeof window.open === "function"
    ) {
        window.open(
            shareUrl,
            "_blank"
        );
    }
}


/* =========================================================
   OPEN GAME BUTTON
========================================================= */

function openGameFromButton() {

    const webApp =
        getTelegramWebApp();

    if (
        webApp &&
        typeof webApp.HapticFeedback !== "undefined"
    ) {

        try {
            webApp.HapticFeedback.impactOccurred(
                "medium"
            );
        } catch (error) {
            // Optional Telegram feature.
        }
    }

    openGamePage();
}


/* =========================================================
   PROFILE BUTTON
========================================================= */

function openProfileFromButton() {

    openProfilePage();
}


/* =========================================================
   MODAL EVENT DELEGATION
========================================================= */

function handleModalClick(event) {

    const closeTarget =
        event.target.closest(
            "[data-close-modal]"
        );

    if (closeTarget) {
        closeModal();
    }
}


/* =========================================================
   NAVIGATION EVENTS
============================
/* ==========================================
   THRONE GAME CONNECTION
========================================== */

function openThroneGame() {
    const game = document.getElementById("throne-game");

    if (!game) {
        console.error("THRONE game container topilmadi.");
        return;
    }

    document
        .querySelectorAll(".page")
        .forEach(page => {
            page.style.display = "none";
        });

    game.style.display = "block";

    if (
        window.THRONE_GAME &&
        typeof window.THRONE_GAME.loadGame === "function"
    ) {
        window.THRONE_GAME.loadGame();
        window.THRONE_GAME.startPolling();
    }
}


function closeThroneGame() {
    const game = document.getElementById("throne-game");

    if (!game) {
        return;
    }

    game.style.display = "none";

    if (
        window.THRONE_GAME &&
        typeof window.THRONE_GAME.stopPolling === "function"
    ) {
        window.THRONE_GAME.stopPolling();
    }
}


window.openThroneGame = openThroneGame;
window.closeThroneGame = closeThroneGame;


/* THRONE game tugmasi */
document.addEventListener("click", event => {

    const button =
        event.target.closest(
            '[data-page="game"], #open-game-button'
        );

    if (!button) {
        return;
    }

    event.preventDefault();

    openThroneGame();
});
