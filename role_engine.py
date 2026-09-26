# ============================================================
# THRONE — ROLE ENGINE
# ============================================================

import random
from roles import get_all_roles, get_role


def assign_roles(player_ids):
    """
    O'yinchilarga rollarni tasodifiy taqsimlaydi.

    Natija:
    [
        {
            "user_id": 123,
            "role_key": "king",
            "side": "Taxt"
        }
    ]
    """

    if not player_ids:
        return []

    roles = list(get_all_roles().keys())

    if len(player_ids) > len(roles):
        raise ValueError(
            f"O'yinchilar soni {len(player_ids)} ta, "
            f"mavjud rollar esa {len(roles)} ta."
        )

    shuffled_players = list(player_ids)
    random.shuffle(shuffled_players)

    shuffled_roles = roles.copy()
    random.shuffle(shuffled_roles)

    assigned = []

    for user_id, role_key in zip(shuffled_players, shuffled_roles):
        role = get_role(role_key)

        assigned.append({
            "user_id": user_id,
            "role_key": role_key,
            "side": role["side"],
        })

    return assigned


def get_player_role(assignments, user_id):
    """
    Berilgan o'yinchining rolini topadi.
    """

    for player in assignments:
        if player["user_id"] == user_id:
            return get_role(player["role_key"])

    return None


def get_player_role_key(assignments, user_id):
    """
    Berilgan o'yinchining role_key qiymatini qaytaradi.
    """

    for player in assignments:
        if player["user_id"] == user_id:
            return player["role_key"]

    return None


def get_player_side(assignments, user_id):
    """
    Berilgan o'yinchining tomonini qaytaradi.
    """

    for player in assignments:
        if player["user_id"] == user_id:
            return player["side"]

    return None


def get_alive_players(assignments, eliminated_ids):
    """
    Eliminatsiya qilingan o'yinchilarni chiqarib tashlab,
    tirik o'yinchilarni qaytaradi.
    """

    eliminated_ids = set(eliminated_ids or [])

    return [
        player
        for player in assignments
        if player["user_id"] not in eliminated_ids
    ]


def get_alive_players_by_side(assignments, eliminated_ids, side):
    """
    Tirik o'yinchilar orasidan ma'lum tomonni qaytaradi.
    """

    alive_players = get_alive_players(
        assignments,
        eliminated_ids
    )

    return [
        player
        for player in alive_players
        if player["side"] == side
    ]


def count_alive_by_side(assignments, eliminated_ids):
    """
    Tirik o'yinchilarni tomonlar bo'yicha sanaydi.
    """

    alive_players = get_alive_players(
        assignments,
        eliminated_ids
    )

    result = {
        "Taxt": 0,
        "Qora": 0,
        "Isyon": 0,
        "Mustaqil": 0,
    }

    for player in alive_players:
        side = player["side"]

        if side not in result:
            result[side] = 0

        result[side] += 1

    return result


def eliminate_player(assignments, eliminated_ids, user_id):
    """
    O'yinchini eliminatsiya qilinganlar ro'yxatiga qo'shadi.
    """

    if eliminated_ids is None:
        eliminated_ids = []

    if user_id not in eliminated_ids:
        eliminated_ids.append(user_id)

    return eliminated_ids


def is_alive(assignments, eliminated_ids, user_id):
    """
    O'yinchi tirik yoki yo'qligini tekshiradi.
    """

    return user_id in [
        player["user_id"]
        for player in get_alive_players(
            assignments,
            eliminated_ids
        )
    ]


def get_role_players(assignments, role_key):
    """
    Ma'lum rolga ega o'yinchilarni qaytaradi.
    """

    return [
        player
        for player in assignments
        if player["role_key"] == role_key
    ]


def get_side_players(assignments, side):
    """
    Ma'lum tomonga tegishli barcha o'yinchilarni qaytaradi.
    """

    return [
        player
        for player in assignments
        if player["side"] == side
    ]


def validate_assignments(assignments):
    """
    Rollar to'g'ri taqsimlanganini tekshiradi.
    """

    if not isinstance(assignments, list):
        return False

    used_users = set()
    used_roles = set()

    for player in assignments:

        if not isinstance(player, dict):
            return False

        if "user_id" not in player:
            return False

        if "role_key" not in player:
            return False

        if "side" not in player:
            return False

        user_id = player["user_id"]
        role_key = player["role_key"]

        if user_id in used_users:
            return False

        if role_key in used_roles:
            return False

        role = get_role(role_key)

        if role is None:
            return False

        if role["side"] != player["side"]:
            return False

        used_users.add(user_id)
        used_roles.add(role_key)

    return True


def get_role_summary(role_key):
    """
    Rol haqida guruh yoki shaxsiy oynada ko'rsatish uchun
    tayyor ma'lumot qaytaradi.
    """

    role = get_role(role_key)

    if not role:
        return None

    return {
        "name": role["name"],
        "side": role["side"],
        "description": role["description"],
        "ability": role["ability"],
        "limitation": role["limitation"],
        "win": role["win"],
  }
