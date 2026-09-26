"use strict";

/*
============================================================
THRONE — MINI APP API
============================================================
Frontend va THRONE backend o‘rtasidagi aloqa qatlami.

Hozir backend URL bo‘sh bo‘lsa, Mini App demo ma'lumotlar
bilan ishlaydi.

Keyinchalik apiBaseUrl Render server manziliga o‘zgartiriladi.
============================================================
*/


const THRONE_API = {

    /* =====================================================
       CONFIG
    ===================================================== */

    getBaseUrl() {

        if (
            typeof THRONE_CONFIG !== "undefined" &&
            THRONE_CONFIG.apiBaseUrl
        ) {
            return THRONE_CONFIG.apiBaseUrl
                .replace(/\/+$/, "");
        }

        return "";
    },


    /* =====================================================
       TELEGRAM DATA
    ===================================================== */

    getTelegramData() {

        if (
            typeof window !== "undefined" &&
            window.Telegram &&
            window.Telegram.WebApp
        ) {
            return (
                window.Telegram.WebApp.initData || ""
            );
        }

        return "";
    },


    /* =====================================================
       HEADERS
    ===================================================== */

    getHeaders() {

        const headers = {
            "Content-Type": "application/json"
        };

        const telegramData =
            this.getTelegramData();

        if (telegramData) {
            headers[
                "X-Telegram-Init-Data"
            ] = telegramData;
        }

        return headers;
    },


    /* =====================================================
       REQUEST
    ===================================================== */

    async request(
        endpoint,
        options = {}
    ) {

        const baseUrl =
            this.getBaseUrl();

        /*
        Backend hali ulanmagan bo‘lsa,
        demo rejim ishlaydi.
        */

        if (!baseUrl) {

            return {
                success: true,
                demo: true,
                data: null
            };
        }


        const cleanEndpoint =
            endpoint.startsWith("/")
                ? endpoint
                : `/${endpoint}`;


        const url =
            `${baseUrl}${cleanEndpoint}`;


        const requestOptions = {
            method:
                options.method || "GET",

            headers: {
                ...this.getHeaders(),
                ...(options.headers || {})
            }
        };


        if (
            options.body !== undefined &&
            options.body !== null
        ) {

            requestOptions.body =
                typeof options.body === "string"
                    ? options.body
                    : JSON.stringify(
                        options.body
                    );
        }


        try {

            const response =
                await fetch(
                    url,
                    requestOptions
                );


            const contentType =
                response.headers.get(
                    "content-type"
                ) || "";


            let result;


            if (
                contentType.includes(
                    "application/json"
                )
            ) {

                result =
                    await response.json();

            } else {

                result =
                    await response.text();
            }


            if (!response.ok) {

                throw new Error(
                    `API error: ${response.status}`
                );
            }


            return result;


        } catch (error) {

            console.error(
                "THRONE API error:",
                error
            );


            return {
                success: false,
                error: error.message,
                data: null
            };
        }
    },


    /* =====================================================
       PLAYER
    ===================================================== */

    async getPlayer() {

        return this.request(
            "/api/player"
        );
    },


    async getProfile() {

        return this.request(
            "/api/profile"
        );
    },


    async getWallet() {

        return this.request(
            "/api/wallet"
        );
    },


    /* =====================================================
       KINGDOM
    ===================================================== */

    async getKingdom() {

        return this.request(
            "/api/kingdom"
        );
    },


    async getCastle() {

        return this.request(
            "/api/castle"
        );
    },


    async getArmy() {

        return this.request(
            "/api/army"
        );
    },


    /* =====================================================
       INVENTORY
    ===================================================== */

    async getInventory() {

        return this.request(
            "/api/inventory"
        );
    },


    async getShop() {

        return this.request(
            "/api/shop"
        );
    },


    async buyItem(itemId) {

        return this.request(
            "/api/shop/buy",
            {
                method: "POST",

                body: {
                    item_id: itemId
                }
            }
        );
    },


    /* =====================================================
       CLAN
    ===================================================== */

    async getClan() {

        return this.request(
            "/api/clan"
        );
    },


    async getClans() {

        return this.request(
            "/api/clans"
        );
    },


    /* =====================================================
       FAMILY
    ===================================================== */

    async getFamily() {

        return this.request(
            "/api/family"
        );
    },


    /* =====================================================
       GAME
    ===================================================== */

    async getActiveGame() {

        return this.request(
            "/api/game"
        );
    },


    async getGameState() {

        return this.request(
            "/api/game/state"
        );
    },


    /* =====================================================
       FRIENDS
    ===================================================== */

    async getFriends() {

        return this.request(
            "/api/friends"
        );
    },


    async addFriend(userId) {

        return this.request(
            "/api/friends/add",
            {
                method: "POST",

                body: {
                    user_id: userId
                }
            }
        );
    },


    /* =====================================================
       RANKING
    ===================================================== */

    async getRanking() {

        return this.request(
            "/api/ranking"
        );
    },


    async getClanRanking() {

        return this.request(
            "/api/ranking/clans"
        );
    },


    /* =====================================================
       REWARDS
    ===================================================== */

    async getRewards() {

        return this.request(
            "/api/rewards"
        );
    },


    async claimDaily() {

        return this.request(
            "/api/daily",
            {
                method: "POST"
            }
        );
    },


    /* =====================================================
       ELITE
    ===================================================== */

    async getElite() {

        return this.request(
            "/api/elite"
        );
    },


    async getElitePlans() {

        return this.request(
            "/api/elite/plans"
        );
    },


    /* =====================================================
       LANGUAGE
    ===================================================== */

    async getLanguage() {

        return this.request(
            "/api/language"
        );
    },


    async setLanguage(language) {

        return this.request(
            "/api/language",
            {
                method: "POST",

                body: {
                    language
                }
            }
        );
    },


    /* =====================================================
       MINI PROFILE
    ===================================================== */

    async getMiniProfile() {

        return this.request(
            "/api/mini/profile"
        );
    },


    async updateMiniProfile(data) {

        return this.request(
            "/api/mini/profile",
            {
                method: "POST",
                body: data
            }
        );
    },


    /* =====================================================
       WORLD
    ===================================================== */

    async getWorldState() {

        return this.request(
            "/api/world"
        );
    },


    /* =====================================================
       HEALTH
    ===================================================== */

    async health() {

        return this.request(
            "/api/health"
        );
    }

};


/* =========================================================
   HELPER FUNCTIONS
========================================================= */


async function apiGet(
    endpoint
) {

    return THRONE_API.request(
        endpoint,
        {
            method: "GET"
        }
    );
}


async function apiPost(
    endpoint,
    data = {}
) {

    return THRONE_API.request(
        endpoint,
        {
            method: "POST",
            body: data
        }
    );
}


/* =========================================================
   EXPORT
========================================================= */

if (
    typeof window !== "undefined"
) {

    window.THRONE_API =
        THRONE_API;

    window.apiGet =
        apiGet;

    window.apiPost =
        apiPost;
  }
