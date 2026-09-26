# ============================================================
# THRONE — GAME ENGINE
# ============================================================

from datetime import datetime
from typing import Optional

from database import (
    get_active_game,
    create_game,
    add_game_player,
    remove_game_player,
    get_game_players,
    set_game_status,
    assign_game_role,
    eliminate_game_player,
    add_game_action,
    add_game_vote,
    get_game_votes,
    clear_game_votes,
    save_game_result,
)

from role_engine import (
    assign_roles,
    get_alive_players,
    get_alive_players_by_side,
    count_alive_by_side,
    get_player_role_key,
)


# ============================================================
# GAME SETTINGS
# ============================================================

MIN_PLAYERS = 7
MAX_PLAYERS = 35

STATUS_LOBBY = "lobby"
STATUS_RUNNING = "running"
STATUS_NIGHT = "night"
STATUS_DAY = "day"
STATUS_VOTING = "voting"
STATUS_FINISHED = "finished"
STATUS_STOPPED = "stopped"


# ============================================================
# BASIC HELPERS
# ============================================================

def get_game(chat_id):
    """
    Guruhdagi faol o'yinni qaytaradi.
    """
    return get_active_game(chat_id)


def game_exists(chat_id):
    """
    Guruhda faol o'yin bor-yo'qligini tekshiradi.
    """
    return get_active_game(chat_id) is not None


def get_players(chat_id):
    """
    Guruhdagi o'yinchilarni qaytaradi.
    """
    game = get_active_game(chat_id)

    if not game:
        return []

    return get_game_players(game["id"])


def get_player_count(chat_id):
    """
    O'yinchilar sonini qaytaradi.
    """
    return len(get_players(chat_id))


def can_join(chat_id, user_id):
    """
    O'yinchi o'yinga qo'shila oladimi?
    """

    game = get_active_game(chat_id)

    if not game:
        return False, "Hozir faol o'yin yo'q."

    if game["status"] != STATUS_LOBBY:
        return False, "O'yin allaqachon boshlangan."

    players = get_game_players(game["id"])

    for player in players:
        if player["user_id"] == user_id:
            return False, "Siz allaqachon o'yindasiz."

    if len(players) >= MAX_PLAYERS:
        return False, "O'yin maksimal o'yinchilar soniga yetdi."

    return True, "OK"


def can_start(chat_id):
    """
    O'yinni boshlash mumkinmi?
    """

    game = get_active_game(chat_id)

    if not game:
        return False, "Faol o'yin mavjud emas."

    if game["status"] != STATUS_LOBBY:
        return False, "O'yin allaqachon boshlangan."

    players = get_game_players(game["id"])

    if len(players) < MIN_PLAYERS:
        return (
            False,
            f"O'yinni boshlash uchun kamida {MIN_PLAYERS} ta "
            f"o'yinchi kerak."
        )

    return True, "OK"


# ============================================================
# CREATE GAME
# ============================================================

async def create_new_game(chat_id, creator_id):
    """
    Yangi guruh o'yinini yaratadi.
    """

    existing = get_active_game(chat_id)

    if existing:
        return {
            "success": False,
            "message": "Bu guruhda allaqachon faol o'yin mavjud.",
        }

    game_id = create_game(
        chat_id=chat_id,
        creator_id=creator_id,
        status=STATUS_LOBBY,
    )

    if not game_id:
        return {
            "success": False,
            "message": "O'yinni yaratishda xatolik yuz berdi.",
        }

    add_game_player(
        game_id=game_id,
        user_id=creator_id,
    )

    return {
        "success": True,
        "game_id": game_id,
        "message": "THRONE o'yini yaratildi.",
    }


# ============================================================
# JOIN
# ============================================================

async def join_game(chat_id, user_id):
    """
    O'yinchini lobbyga qo'shadi.
    """

    allowed, message = can_join(chat_id, user_id)

    if not allowed:
        return {
            "success": False,
            "message": message,
        }

    game = get_active_game(chat_id)

    add_game_player(
        game_id=game["id"],
        user_id=user_id,
    )

    players = get_game_players(game["id"])

    return {
        "success": True,
        "game_id": game["id"],
        "players": players,
        "count": len(players),
        "message": "Siz THRONE o'yiniga qo'shildingiz.",
    }


# ============================================================
# LEAVE
# ============================================================

async def leave_game(chat_id, user_id):
    """
    Lobbydan chiqish.
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "success": False,
            "message": "Faol o'yin mavjud emas.",
        }

    if game["status"] != STATUS_LOBBY:
        return {
            "success": False,
            "message": "O'yin boshlanganidan keyin lobbydan chiqib bo'lmaydi.",
        }

    players = get_game_players(game["id"])

    exists = any(
        player["user_id"] == user_id
        for player in players
    )

    if not exists:
        return {
            "success": False,
            "message": "Siz o'yinda emassiz.",
        }

    remove_game_player(
        game_id=game["id"],
        user_id=user_id,
    )

    return {
        "success": True,
        "message": "Siz o'yindan chiqdingiz.",
    }


# ============================================================
# START GAME
# ============================================================

async def start_game(chat_id):
    """
    Lobbydan haqiqiy o'yin bosqichiga o'tadi.
    """

    allowed, message = can_start(chat_id)

    if not allowed:
        return {
            "success": False,
            "message": message,
        }

    game = get_active_game(chat_id)
    players = get_game_players(game["id"])

    player_ids = [
        player["user_id"]
        for player in players
    ]

    assignments = assign_roles(player_ids)

    if not assignments:
        return {
            "success": False,
            "message": "Rollarni taqsimlashda xatolik.",
        }

    for assignment in assignments:
        assign_game_role(
            game_id=game["id"],
            user_id=assignment["user_id"],
            role_key=assignment["role_key"],
        )

    set_game_status(
        game_id=game["id"],
        status=STATUS_RUNNING,
    )

    set_game_status(
        game_id=game["id"],
        status=STATUS_NIGHT,
    )

    return {
        "success": True,
        "game_id": game["id"],
        "status": STATUS_NIGHT,
        "players": assignments,
        "message": "THRONE o'yini boshlandi. Birinchi tun boshlandi.",
    }


# ============================================================
# NIGHT
# ============================================================

async def start_night(chat_id):
    """
    Yangi tun bosqichini boshlaydi.
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "success": False,
            "message": "Faol o'yin mavjud emas.",
        }

    if game["status"] not in (
        STATUS_RUNNING,
        STATUS_DAY,
    ):
        return {
            "success": False,
            "message": "Hozir tun bosqichini boshlash mumkin emas.",
        }

    set_game_status(
        game_id=game["id"],
        status=STATUS_NIGHT,
    )

    return {
        "success": True,
        "status": STATUS_NIGHT,
        "message": "🌙 Tun boshlandi.",
    }


# ============================================================
# NIGHT ACTION
# ============================================================

async def submit_night_action(
    chat_id,
    user_id,
    action_type,
    target_id=None,
    value=None,
):
    """
    Tungi harakatni saqlaydi.

    action_type:
    protect
    attack
    inspect
    poison
    trap
    track
    etc.
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "success": False,
            "message": "Faol o'yin mavjud emas.",
        }

    if game["status"] != STATUS_NIGHT:
        return {
            "success": False,
            "message": "Hozir tun emas.",
        }

    players = get_game_players(game["id"])

    player = next(
        (
            p for p in players
            if p["user_id"] == user_id
        ),
        None,
    )

    if not player:
        return {
            "success": False,
            "message": "Siz bu o'yinda emassiz.",
        }

    if player.get("is_alive", 1) == 0:
        return {
            "success": False,
            "message": "Siz o'yindan chiqarilgansiz.",
        }

    add_game_action(
        game_id=game["id"],
        user_id=user_id,
        action_type=action_type,
        target_id=target_id,
        value=value,
    )

    return {
        "success": True,
        "message": "Tungi harakatingiz qabul qilindi.",
    }


# ============================================================
# DAY
# ============================================================

async def start_day(chat_id):
    """
    Tongni boshlaydi.
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "success": False,
            "message": "Faol o'yin mavjud emas.",
        }

    if game["status"] != STATUS_NIGHT:
        return {
            "success": False,
            "message": "Hozir tongni boshlash mumkin emas.",
        }

    set_game_status(
        game_id=game["id"],
        status=STATUS_DAY,
    )

    return {
        "success": True,
        "status": STATUS_DAY,
        "message": "☀️ Tong otdi.",
    }


# ============================================================
# VOTING
# ============================================================

async def start_voting(chat_id):
    """
    Kunlik ovoz berishni boshlaydi.
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "success": False,
            "message": "Faol o'yin mavjud emas.",
        }

    if game["status"] != STATUS_DAY:
        return {
            "success": False,
            "message": "Hozir ovoz berishni boshlash mumkin emas.",
        }

    clear_game_votes(game["id"])

    set_game_status(
        game_id=game["id"],
        status=STATUS_VOTING,
    )

    return {
        "success": True,
        "status": STATUS_VOTING,
        "message": "⚖️ Ovoz berish boshlandi.",
    }


async def submit_vote(chat_id, voter_id, target_id):
    """
    O'yinchi ovozini beradi.
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "success": False,
            "message": "Faol o'yin mavjud emas.",
        }

    if game["status"] != STATUS_VOTING:
        return {
            "success": False,
            "message": "Hozir ovoz berish bosqichi emas.",
        }

    players = get_game_players(game["id"])

    voter = next(
        (
            p for p in players
            if p["user_id"] == voter_id
        ),
        None,
    )

    target = next(
        (
            p for p in players
            if p["user_id"] == target_id
        ),
        None,
    )

    if not voter:
        return {
            "success": False,
            "message": "Siz o'yinda emassiz.",
        }

    if not target:
        return {
            "success": False,
            "message": "Tanlangan o'yinchi topilmadi.",
        }

    if voter.get("is_alive", 1) == 0:
        return {
            "success": False,
            "message": "Eliminatsiya qilingan o'yinchi ovoz bera olmaydi.",
        }

    if target.get("is_alive", 1) == 0:
        return {
            "success": False,
            "message": "Eliminatsiya qilingan o'yinchiga ovoz berib bo'lmaydi.",
        }

    if voter_id == target_id:
        return {
            "success": False,
            "message": "O'zingizga ovoz bera olmaysiz.",
        }

    add_game_vote(
        game_id=game["id"],
        voter_id=voter_id,
        target_id=target_id,
    )

    return {
        "success": True,
        "message": "Ovozingiz qabul qilindi.",
    }


# ============================================================
# RESOLVE VOTING
# ============================================================

def resolve_voting(chat_id):
    """
    Ovozlarni hisoblaydi.

    Eng ko'p ovoz olgan o'yinchi:
    - yagona ko'pchilik bo'lsa -> eliminatsiya
    - tenglik bo'lsa -> revote
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "success": False,
            "message": "Faol o'yin mavjud emas.",
        }

    votes = get_game_votes(game["id"])

    if not votes:
        return {
            "success": False,
            "message": "Hech kim ovoz bermadi.",
        }

    counts = {}

    for vote in votes:
        target_id = vote["target_id"]

        counts[target_id] = counts.get(
            target_id,
            0,
        ) + 1

    if not counts:
        return {
            "success": False,
            "message": "Ovozlar topilmadi.",
        }

    highest = max(counts.values())

    winners = [
        user_id
        for user_id, count in counts.items()
        if count == highest
    ]

    # Teng ovoz
    if len(winners) > 1:
        clear_game_votes(game["id"])

        return {
            "success": True,
            "eliminated": None,
            "tie": True,
            "revote": True,
            "message": "⚖️ Ovozlar teng bo'ldi. Qayta ovoz beriladi.",
        }

    eliminated_id = winners[0]

    eliminate_game_player(
        game_id=game["id"],
        user_id=eliminated_id,
    )

    clear_game_votes(game["id"])

    return {
        "success": True,
        "eliminated": eliminated_id,
        "tie": False,
        "revote": False,
        "message": "Ovoz berish yakunlandi.",
    }


# ============================================================
# ELIMINATION
# ============================================================

async def eliminate_player(
    chat_id,
    user_id,
    reason="vote",
):
    """
    O'yinchini o'yindan chiqaradi.
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "success": False,
            "message": "Faol o'yin mavjud emas.",
        }

    players = get_game_players(game["id"])

    player = next(
        (
            p for p in players
            if p["user_id"] == user_id
        ),
        None,
    )

    if not player:
        return {
            "success": False,
            "message": "O'yinchi topilmadi.",
        }

    if player.get("is_alive", 1) == 0:
        return {
            "success": False,
            "message": "O'yinchi allaqachon chiqarilgan.",
        }

    eliminate_game_player(
        game_id=game["id"],
        user_id=user_id,
    )

    add_game_action(
        game_id=game["id"],
        user_id=user_id,
        action_type="eliminated",
        target_id=user_id,
        value=reason,
    )

    return {
        "success": True,
        "user_id": user_id,
        "reason": reason,
        "message": "O'yinchi eliminatsiya qilindi.",
    }


# ============================================================
# LAST WORDS
# ============================================================

def create_last_words(user_id):
    """
    Oxirgi so'z uchun standart THRONE matni.
    """

    return (
        "👑 THRONE yo'lida mening so'nggi so'zim:\n\n"
        "⚔️ Haqiqat vaqt bilan ochiladi.\n"
        "🏰 Taxt esa hali o'z egasini kutmoqda."
    )


# ============================================================
# ALIVE PLAYERS
# ============================================================

def get_alive_game_players(chat_id):
    """
    Hozir tirik o'yinchilarni qaytaradi.
    """

    game = get_active_game(chat_id)

    if not game:
        return []

    players = get_game_players(game["id"])

    return [
        player
        for player in players
        if player.get("is_alive", 1) == 1
    ]


# ============================================================
# WIN CONDITION
# ============================================================

def check_victory(chat_id):
    """
    G'alaba shartlarini tekshiradi.

    Taxt, Qora va Isyon tomonlari bo'yicha
    tirik o'yinchilar sonini hisoblaydi.
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "finished": False,
            "winner": None,
        }

    players = get_game_players(game["id"])

    alive = [
        player
        for player in players
        if player.get("is_alive", 1) == 1
    ]

    side_counts = {
        "Taxt": 0,
        "Qora": 0,
        "Isyon": 0,
        "Mustaqil": 0,
    }

    for player in alive:
        role_key = player.get("role_key")

        if not role_key:
            continue

        role = get_role_key_info(role_key)

        if not role:
            continue

        side = role["side"]

        if side not in side_counts:
            side_counts[side] = 0

        side_counts[side] += 1

    # Mustaqil g'olibliklari keyinchalik
    # maxsus shartlar orqali kengaytiriladi.

    taxt = side_counts["Taxt"]
    qora = side_counts["Qora"]
    isyon = side_counts["Isyon"]

    # Qora va Isyon qolmagan bo'lsa — Taxt
    if qora == 0 and isyon == 0 and taxt > 0:
        return {
            "finished": True,
            "winner": "Taxt",
            "side_counts": side_counts,
        }

    # Taxt qolmasa va Qora ko'pchilikka ega bo'lsa
    if taxt == 0 and isyon == 0 and qora > 0:
        return {
            "finished": True,
            "winner": "Qora",
            "side_counts": side_counts,
        }

    # Taxt qolmasa va Isyon ustun qolsa
    if taxt == 0 and qora == 0 and isyon > 0:
        return {
            "finished": True,
            "winner": "Isyon",
            "side_counts": side_counts,
        }

    return {
        "finished": False,
        "winner": None,
        "side_counts": side_counts,
    }


def get_role_key_info(role_key):
    """
    role_engine orqali rol ma'lumotini olish uchun
    ichki yordamchi.
    """

    from roles import get_role

    return get_role(role_key)


# ============================================================
# FINISH GAME
# ============================================================

async def finish_game(chat_id, winner):
    """
    O'yinni yakunlaydi.
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "success": False,
            "message": "Faol o'yin mavjud emas.",
        }

    set_game_status(
        game_id=game["id"],
        status=STATUS_FINISHED,
    )

    save_game_result(
        game_id=game["id"],
        winner=winner,
    )

    return {
        "success": True,
        "winner": winner,
        "message": f"👑 THRONE o'yini yakunlandi. G'olib tomon: {winner}",
    }


# ============================================================
# STOP GAME
# ============================================================

async def stop_game(chat_id):
    """
    O'yinni majburiy to'xtatadi.
    """

    game = get_active_game(chat_id)

    if not game:
        return {
            "success": False,
            "message": "Faol o'yin mavjud emas.",
        }

    set_game_status(
        game_id=game["id"],
        status=STATUS_STOPPED,
    )

    return {
        "success": True,
        "message": "THRONE o'yini to'xtatildi.",
    }


# ============================================================
# GAME SUMMARY
# ============================================================

def get_game_summary(chat_id):
    """
    Guruh o'yini haqida umumiy ma'lumot.
    """

    game = get_active_game(chat_id)

    if not game:
        return None

    players = get_game_players(game["id"])

    alive = [
        player
        for player in players
        if player.get("is_alive", 1) == 1
    ]

    eliminated = [
        player
        for player in players
        if 
