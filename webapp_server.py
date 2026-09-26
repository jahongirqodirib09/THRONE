import json
import logging
from aiohttp import web

from config import BOT_TOKEN
from database import (
    get_user,
    get_player_stats,
    get_kingdom,
    get_castle,
    get_army,
    get_inventory,
    get_active_game,
    get_game_players,
    get_top_players,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("THRONE_WEBAPP")


# ============================================================
# HELPERS
# ============================================================

def json_response(data, status=200):
    return web.json_response(
        data,
        status=status,
        dumps=lambda value: json.dumps(
            value,
            ensure_ascii=False
        ),
    )


def get_init_data(request):
    return request.headers.get(
        "X-Telegram-Init-Data",
        ""
    ).strip()


def get_user_id(request):
    """
    Hozircha Mini App so'rovlaridagi
    X-Telegram-User-Id headeridan foydalanadi.

    Keyingi bosqichda Telegram WebApp
    initData cryptographic validation ham qo'shiladi.
    """

    value = request.headers.get(
        "X-Telegram-User-Id",
        ""
    ).strip()

    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


async def require_user(request):
    user_id = get_user_id(request)

    if user_id <= 0:
        return None

    return user_id


# ============================================================
# HEALTH
# ============================================================

async def health(request):
    return json_response({
        "success": True,
        "service": "THRONE",
        "status": "online",
        "webapp": True,
    })


# ============================================================
# PROFILE
# ============================================================

async def player_profile(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Telegram foydalanuvchisi aniqlanmadi."
            },
            401
        )

    user = await get_user(user_id)
    stats = await get_player_stats(user_id)

    if not user:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi topilmadi."
            },
            404
        )

    return json_response({
        "success": True,
        "player": user,
        "stats": stats,
    })


# ============================================================
# WALLET
# ============================================================

async def wallet(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi aniqlanmadi."
            },
            401
        )

    user = await get_user(user_id)

    if not user:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi topilmadi."
            },
            404
        )

    return json_response({
        "success": True,
        "wallet": {
            "gold": user.get("gold", 0),
            "coin": user.get("coin", 0),
            "diamond": user.get("diamond", 0),
            "elite": user.get("elite_active", False),
        }
    })


# ============================================================
# KINGDOM
# ============================================================

async def kingdom(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi aniqlanmadi."
            },
            401
        )

    kingdom_data = await get_kingdom(user_id)

    return json_response({
        "success": True,
        "kingdom": kingdom_data,
    })


# ============================================================
# CASTLE
# ============================================================

async def castle(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi aniqlanmadi."
            },
            401
        )

    castle_data = await get_castle(user_id)

    return json_response({
        "success": True,
        "castle": castle_data,
    })


# ============================================================
# ARMY
# ============================================================

async def army(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi aniqlanmadi."
            },
            401
        )

    army_data = await get_army(user_id)

    return json_response({
        "success": True,
        "army": army_data,
    })


# ============================================================
# INVENTORY
# ============================================================

async def inventory(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi aniqlanmadi."
            },
            401
        )

    items = await get_inventory(user_id)

    return json_response({
        "success": True,
        "inventory": items,
    })


# ============================================================
# ACTIVE GAME
# ============================================================

async def game_state(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi aniqlanmadi."
            },
            401
        )

    game = await get_active_game()

    if not game:
        return json_response({
            "success": True,
            "active": False,
            "game": None,
        })

    players = await get_game_players(
        game["id"]
    )

    safe_players = []

    for player in players:

        safe_players.append({
            "id": player.get("user_id"),
            "name": player.get(
                "first_name",
                "O‘yinchi"
            ),
            "alive": player.get(
                "is_alive",
                True
            ),
        })

    return json_response({
        "success": True,
        "active": True,
        "game": {
            "id": game.get("id"),
            "game_id": game.get("id"),
            "status": game.get("status"),
            "phase": game.get("status"),
            "players": safe_players,
            "alive_players": [
                player
                for player in safe_players
                if player["alive"]
            ],
            "eliminated_players": [
                player
                for player in safe_players
                if not player["alive"]
            ],

            # Muhim:
            # Boshqa o'yinchilarga yashirin rol berilmaydi.
            "my_role": None,
            "my_side": None,
        }
    })


# ============================================================
# JOIN GAME
# ============================================================

async def join_game(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi aniqlanmadi."
            },
            401
        )

    try:
        body = await request.json()
    except Exception:
        body = {}

    game_id = body.get("game_id")

    if not game_id:
        return json_response(
            {
                "success": False,
                "error": "game_id kerak."
            },
            400
        )

    # Guruhdagi asosiy /join tizimi bilan
    # keyinchalik to'g'ridan-to'g'ri bog'lanadi.

    return json_response({
        "success": True,
        "message": "O‘yinga qo‘shilish so‘rovi qabul qilindi.",
        "user_id": user_id,
        "game_id": game_id,
    })


# ============================================================
# GAME ACTION
# ============================================================

async def game_action(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi aniqlanmadi."
            },
            401
        )

    try:
        body = await request.json()
    except Exception:
        body = {}

    game_id = body.get("game_id")
    action = body.get("action")
    target_id = body.get("target_id")

    if not game_id:
        return json_response(
            {
                "success": False,
                "error": "game_id kerak."
            },
            400
        )

    if not action:
        return json_response(
            {
                "success": False,
                "error": "action kerak."
            },
            400
        )

    allowed_actions = {
        "observe",
        "protect",
        "block",
        "poison",
        "weaken",
        "attack",
        "special",
    }

    if action not in allowed_actions:
        return json_response(
            {
                "success": False,
                "error": "Noto‘g‘ri harakat."
            },
            400
        )

    return json_response({
        "success": True,
        "message": "Harakat qabul qilindi.",
        "user_id": user_id,
        "game_id": game_id,
        "action": action,
        "target_id": target_id,
    })


# ============================================================
# VOTE
# ============================================================

async def game_vote(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi aniqlanmadi."
            },
            401
        )

    try:
        body = await request.json()
    except Exception:
        body = {}

    game_id = body.get("game_id")
    target_id = body.get("target_id")

    if not game_id or not target_id:
        return json_response(
            {
                "success": False,
                "error": "game_id va target_id kerak."
            },
            400
        )

    return json_response({
        "success": True,
        "message": "Ovoz qabul qilindi.",
        "user_id": user_id,
        "game_id": game_id,
        "target_id": target_id,
    })


# ============================================================
# RANKING
# ============================================================

async def ranking(request):

    players = await get_top_players(
        limit=100
    )

    return json_response({
        "success": True,
        "ranking": players,
    })


# ============================================================
# FRIENDS
# ============================================================

async def friends(request):

    user_id = await require_user(request)

    if not user_id:
        return json_response(
            {
                "success": False,
                "error": "Foydalanuvchi aniqlanmadi."
            },
            401
        )

    return json_response({
        "success": True,
        "friends": [],
    })


# ============================================================
# WORLD
# ============================================================

async def world(request):

    return json_response({
        "success": True,
        "world": {
            "phase": "day",
            "time": "day",
            "weather": "clear",
            "season": "autumn",
        }
    })


# ============================================================
# ROUTES
# ============================================================

def create_app():

    app = web.Application()

    app.router.add_get(
        "/api/health",
        health
    )

    app.router.add_get(
        "/api/player",
        player_profile
    )

    app.router.add_get(
        "/api/profile",
        player_profile
    )

    app.router.add_get(
        "/api/wallet",
        wallet
    )

    app.router.add_get(
        "/api/kingdom",
        kingdom
    )

    app.router.add_get(
        "/api/castle",
        castle
    )

    app.router.add_get(
        "/api/army",
        army
    )

    app.router.add_get(
        "/api/inventory",
        inventory
    )

    app.router.add_get(
        "/api/game",
        game_state
    )

    app.router.add_get(
        "/api/game/state",
        game_state
    )

    app.router.add_post(
        "/api/game/join",
        join_game
    )

    app.router.add_post(
        "/api/game/action",
        game_action
    )

    app.router.add_post(
        "/api/game/vote",
        game_vote
    )

    app.router.add_get(
        "/api/ranking",
        ranking
    )

    app.router.add_get(
        "/api/friends",
        friends
    )

    app.router.add_get(
        "/api/world",
        world
    )

    return app


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    import os

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )

    app = create_app()

    logger.info(
        "THRONE WebApp API ishga tushmoqda: port %s",
        port
    )

    web.run_app(
        app,
        host="0.0.0.0",
        port=port
)
