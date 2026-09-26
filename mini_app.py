# ============================================================
# THRONE — MINI APP BACKEND
# ============================================================

from dataclasses import dataclass
from typing import Optional

from config import CREATOR_ID
from database import (
    get_user,
    get_mini_profile,
    update_mini_profile,
    get_inventory,
)


# ============================================================
# CONSTANTS
# ============================================================

MIN_LEVEL = 1
MAX_LEVEL = 100

DAY = "day"
NIGHT = "night"

STATUS_ONLINE = "online"
STATUS_OFFLINE = "offline"

MAX_FRIENDS = 500


# ============================================================
# CHARACTER TYPES
# ============================================================

CHARACTERS = {
    "king": {
        "name": "👑 Qirol",
        "title": "Taxt egasi",
        "description": "Qirollik hukmdori.",
        "avatar": "king",
        "background": "royal_castle",
    },
    "queen": {
        "name": "👸 Malika",
        "title": "Saroy malikasi",
        "description": "Qirollik saroyining vakili.",
        "avatar": "queen",
        "background": "royal_palace",
    },
    "commander": {
        "name": "⚔️ Qo‘mondon",
        "title": "Bosh qo‘mondon",
        "description": "Qirollik qo‘shinlari yetakchisi.",
        "avatar": "commander",
        "background": "war_camp",
    },
    "noble": {
        "name": "🏰 Zodagon",
        "title": "Qirollik zodagoni",
        "description": "Saroyning nufuzli vakili.",
        "avatar": "noble",
        "background": "noble_hall",
    },
    "knight": {
        "name": "🛡️ Ritsar",
        "title": "Qirollik ritsari",
        "description": "Qirollik himoyachisi.",
        "avatar": "knight",
        "background": "castle_gate",
    },
    "hunter": {
        "name": "🏹 Ovchi",
        "title": "Qirollik ovchisi",
        "description": "Chegaralarni kuzatuvchi jangchi.",
        "avatar": "hunter",
        "background": "forest",
    },
}


# ============================================================
# CLOTHING
# ============================================================

CLOTHING = {
    "basic": {
        "name": "Oddiy kiyim",
        "rarity": "common",
        "bonus": 0,
    },
    "noble": {
        "name": "Zodagon kiyimi",
        "rarity": "rare",
        "bonus": 5,
    },
    "royal": {
        "name": "Qirollik kiyimi",
        "rarity": "epic",
        "bonus": 10,
    },
    "throne": {
        "name": "THRONE libosi",
        "rarity": "legendary",
        "bonus": 20,
    },
}


# ============================================================
# WEAPONS
# ============================================================

WEAPONS = {
    "none": {
        "name": "Qurolsiz",
        "attack": 0,
    },
    "sword": {
        "name": "Temir qilich",
        "attack": 10,
    },
    "royal_sword": {
        "name": "Qirollik qilichi",
        "attack": 25,
    },
    "throne_blade": {
        "name": "THRONE Blade",
        "attack": 50,
    },
}


# ============================================================
# HORSES
# ============================================================

HORSES = {
    "none": {
        "name": "Ot yo‘q",
        "speed": 0,
    },
    "brown": {
        "name": "Jigarrang ot",
        "speed": 10,
    },
    "black": {
        "name": "Qora ot",
        "speed": 25,
    },
    "royal": {
        "name": "Qirollik oti",
        "speed": 40,
    },
    "throne": {
        "name": "THRONE oti",
        "speed": 60,
    },
}


# ============================================================
# RESULT
# ============================================================

@dataclass
class MiniAppResult:
    success: bool
    message: str
    data: Optional[dict] = None


# ============================================================
# CREATOR
# ============================================================

def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


# ============================================================
# CHARACTER HELPERS
# ============================================================

def get_character(character_id: str) -> Optional[dict]:
    return CHARACTERS.get(character_id)


def character_exists(character_id: str) -> bool:
    return character_id in CHARACTERS


def get_all_characters() -> dict:
    return {
        key: dict(value)
        for key, value in CHARACTERS.items()
    }


# ============================================================
# CHARACTER SELECTION
# ============================================================

async def choose_character(
    user_id: int,
    character_id: str,
) -> MiniAppResult:

    if not character_exists(character_id):
        return MiniAppResult(
            False,
            "❌ Bunday qahramon mavjud emas.",
        )

    user = await get_user(user_id)

    if not user:
        return MiniAppResult(
            False,
            "❌ O‘yinchi topilmadi.",
        )

    profile = await get_mini_profile(user_id)

    if profile:
        existing_character = (
            profile.get("character_id")
            if isinstance(profile, dict)
            else None
        )

        if existing_character:
            return MiniAppResult(
                False,
                (
                    "⚠️ Qahramon allaqachon tanlangan.\n\n"
                    "THRONE’da qahramonni keyinchalik "
                    "almashtirib bo‘lmaydi."
                ),
            )

    try:
        result = await update_mini_profile(
            user_id,
            character_id=character_id,
        )
    except TypeError:
        return MiniAppResult(
            False,
            "❌ Mini App profilini saqlashda xatolik.",
        )

    character = get_character(character_id)

    return MiniAppResult(
        True,
        (
            "👑 QAHRAMON TANLANDI\n\n"
            f"{character['name']}\n"
            f"🏷️ {character['title']}\n\n"
            "Bu tanlov Mini App ko‘rinishiga ta’sir qiladi.\n"
            "🎮 Guruhdagi o‘yin jarayoniga ta’sir qilmaydi."
        ),
        {
            "character_id": character_id,
            "character": character,
            "result": result,
        },
    )


# ============================================================
# LEVEL
# ============================================================

def normalize_level(level) -> int:

    try:
        level = int(level)
    except (
        TypeError,
        ValueError,
    ):
        level = MIN_LEVEL

    return max(
        MIN_LEVEL,
        min(
            MAX_LEVEL,
            level,
        ),
    )


def level_progress(level: int) -> dict:

    level = normalize_level(level)

    progress = int(
        ((level - 1) / (MAX_LEVEL - 1)) * 100
    )

    return {
        "level": level,
        "progress": progress,
        "next_level": (
            level + 1
            if level < MAX_LEVEL
            else MAX_LEVEL
        ),
    }


# ============================================================
# DAY / NIGHT
# ============================================================

def get_world_phase(hour: int) -> str:

    try:
        hour = int(hour)
    except (
        TypeError,
        ValueError,
    ):
        hour = 12

    hour %= 24

    if 6 <= hour < 18:
        return DAY

    return NIGHT


def world_phase_data(
    phase: str,
) -> dict:

    if phase == NIGHT:
        return {
            "phase": NIGHT,
            "name": "🌙 Tun",
            "sky": "night",
            "castle_lights": True,
            "stars": True,
        }

    return {
        "phase": DAY,
        "name": "☀️ Kun",
        "sky": "day",
        "castle_lights": False,
        "stars": False,
    }


# ============================================================
# ONLINE STATUS
# ============================================================

def normalize_status(
    online: bool,
) -> str:

    return (
        STATUS_ONLINE
        if online
        else STATUS_OFFLINE
    )


def status_text(
    online: bool,
) -> str:

    if online:
        return "🟢 Online"

    return "⚫ Offline"


# ============================================================
# FRIENDS
# ============================================================

def can_add_friend(
    current_count: int,
) -> bool:

    return (
        int(current_count)
        < MAX_FRIENDS
    )


def friend_data(
    user_id: int,
    name: str,
    online: bool = False,
) -> dict:

    return {
        "user_id": int(user_id),
        "name": name,
        "status": normalize_status(
            online
        ),
        "status_text": status_text(
            online
        ),
    }


# ============================================================
# AVATAR
# ============================================================

def build_avatar(
    character_id: str,
    level: int = 1,
) -> dict:

    character = get_character(
        character_id
    )

    if not character:
        character = CHARACTERS["noble"]
        character_id = "noble"

    return {
        "character_id": character_id,
        "name": character["name"],
        "avatar": character["avatar"],
        "background": character["background"],
        "level": normalize_level(level),
    }


# ============================================================
# EQUIPMENT
# ============================================================

def get_clothing(
    clothing_id: str,
) -> dict:

    return CLOTHING.get(
        clothing_id,
        CLOTHING["basic"],
    )


def get_weapon(
    weapon_id: str,
) -> dict:

    return WEAPONS.get(
        weapon_id,
        WEAPONS["none"],
    )


def get_horse(
    horse_id: str,
) -> dict:

    return HORSES.get(
        horse_id,
        HORSES["none"],
    )


# ============================================================
# EQUIPMENT POWER
# ============================================================

def calculate_equipment_power(
    clothing_id: str = "basic",
    weapon_id: str = "none",
    horse_id: str = "none",
) -> dict:

    clothing = get_clothing(
        clothing_id
    )

    weapon = get_weapon(
        weapon_id
    )

    horse = get_horse(
        horse_id
    )

    attack = (
        weapon.get(
            "attack",
            0,
        )
    )

    defense = (
        clothing.get(
            "bonus",
            0,
        )
    )

    speed = (
        horse.get(
            "speed",
            0,
        )
    )

    return {
        "attack": attack,
        "defense": defense,
        "speed": speed,
        "total": (
            attack
            + defense
            + speed
        ),
    }


# ============================================================
# INVENTORY EQUIPMENT DETECTION
# ============================================================

def find_inventory_item(
    inventory,
    item_id: str,
) -> int:

    if not inventory:
        return 0

    if isinstance(
        inventory,
        dict,
    ):

        item = inventory.get(
            item_id
        )

        if isinstance(
            item,
            int,
        ):
            return item

        if isinstance(
            item,
            dict,
        ):
            return int(
                item.get(
                    "quantity",
                    0,
                )
                or 0
            )

    if isinstance(
        inventory,
        list,
    ):

        total = 0

        for row in inventory:

            if not isinstance(
                row,
                dict,
            ):
                continue

            if row.get(
                "item_id"
            ) == item_id:

                total += int(
                    row.get(
                        "quantity",
                        0,
                    )
                    or 0
                )

        return total

    return 0


# ============================================================
# PROFILE
# ============================================================

async def get_mini_profile_data(
    user_id: int,
) -> MiniAppResult:

    user = await get_user(
        user_id
    )

    if not user:
        return MiniAppResult(
            False,
            "❌ O‘yinchi topilmadi.",
        )

    profile = await get_mini_profile(
        user_id
    )

    if not isinstance(
        profile,
        dict,
    ):
        profile = {}

    first_name = (
        user.get(
            "first_name",
            "O‘yinchi",
        )
        if isinstance(
            user,
            dict,
        )
        else "O‘yinchi"
    )

    username = (
        user.get(
            "username",
            "",
        )
        if isinstance(
            user,
            dict,
        )
        else ""
    )

    level = normalize_level(
        profile.get(
            "level",
            1,
        )
    )

    character_id = profile.get(
        "character_id"
    )

    character = (
        get_character(
            character_id
        )
        if character_id
        else None
    )

    if not character:
        character_id = "noble"
        character = CHARACTERS["noble"]

    avatar = build_avatar(
        character_id,
        level,
    )

    return MiniAppResult(
        True,
        "✅ Mini App profili tayyor.",
        {
            "user_id": user_id,
            "first_name": first_name,
            "username": username,
            "level": level,
            "level_progress": level_progress(
                level
            ),
            "character": avatar,
            "online": True,
            "status": STATUS_ONLINE,
        },
    )


# ============================================================
# COMPLETE MINI APP STATE
# ============================================================

async def get_mini_app_state(
    user_id: int,
    hour: int = 12,
) -> MiniAppResult:

    profile_result = await get_mini_profile_data(
        user_id
    )

    if not profile_result.success:
        return profile_result

    inventory = await get_inventory(
        user_id
    )

    data = profile_result.data

    phase = get_world_phase(
        hour
    )

    world = world_phase_data(
        phase
    )

    equipment = {
        "clothing": "basic",
        "weapon": "none",
        "horse": "none",
    }

    power = calculate_equipment_power(
        equipment["clothing"],
        equipment["weapon"],
        equipment["horse"],
    )

    return MiniAppResult(
        True,
        "👑 THRONE Mini App holati tayyor.",
        {
            "player": data,
            "world": world,
            "equipment": equipment,
            "equipment_power": power,
            "inventory": inventory or [],
            "features": {
                "live_world": True,
                "day_night": True,
                "avatar": True,
                "level_system": True,
                "equipment": True,
                "horses": True,
                "friends": True,
                "online_status": True,
                "group_game": True,
            },
        },
    )


# ============================================================
# LOBBY
# ============================================================

def lobby_characters() -> list:

    return [
        {
            "slot": 1,
            "animation": "idle",
            "character": "king",
            "action": "fist_to_chest",
        },
        {
            "slot": 2,
            "animation": "idle",
            "character": "commander",
            "action": "wave",
        },
        {
            "slot": 3,
            "animation": "idle",
            "character": "noble",
            "action": "idle",
        },
        {
            "slot": 4,
            "animation": "idle",
            "character": "knight",
            "action": "wave",
        },
    ]


def lobby_data() -> dict:

    return {
        "title": "👑 THRONE",
        "subtitle": "Qirollik seni kutmoqda.",
        "characters": lobby_characters(),
        "music": {
            "enabled": True,
            "type": "royal_ambient",
            "copyright_safe": True,
        },
        "animations": {
            "idle": True,
            "wave": True,
            "fist_to_chest": True,
            "bow": False,
        },
    }


# ============================================================
# GROUP GAME VIEW
# ============================================================

def group_game_view(
    game_data: Optional[dict] = None,
) -> dict:

    if not game_data:
        return {
            "active": False,
            "message": "Hozir faol guruh o‘yini yo‘q.",
        }

    return {
        "active": True,
        "game_id": game_data.get(
            "id"
        ),
        "status": game_data.get(
            "status",
            "unknown",
        ),
        "players": game_data.get(
            "players",
            [],
        ),
        "phase": game_data.get(
            "phase",
            "unknown",
        ),
        "show_in_mini_app": True,
    }


# ============================================================
# PROFILE UPDATE
# ============================================================

async def update_profile(
    user_id: int,
    **fields,
) -> MiniAppResult:

    allowed = {
        "level",
        "character_id",
        "clothing_id",
        "weapon_id",
        "horse_id",
        "background_id",
    }

    clean = {}

    for key, value in fields.items():

        if key not in allowed:
            continue

        if key == "level":
            value = normalize_level(
                value
            )

        clean[key] = value

    if not clean:
        return MiniAppResult(
            False,
            "❌ Yangilanadigan ma’lumot yo‘q.",
        )

    try:

        result = await update_mini_profile(
            user_id,
            **clean,
        )

    except TypeError:

        return MiniAppResult(
            False,
            "❌ Profilni yangilashda xatolik.",
        )

    return MiniAppResult(
        True,
        "✅ Mini App profili yangilandi.",
        {
            "updated": clean,
            "result": result,
        },
    )


# ============================================================
# LEVEL UP
# ============================================================

async def set_level(
    user_id: int,
    level: int,
) -> MiniAppResult:

    level = normalize_level(
        level
    )

    return await update_profile(
        user_id,
        level=level,
    )


# ============================================================
# MINI APP HOME
# ============================================================

async def mini_app_home(
    user_id: int,
    hour: int = 12,
) -> dict:

    state = await get_mini_app_state(
        user_id,
        hour,
    )

    if not state.success:
        return {
            "success": False,
            "message": state.message,
        }

    return {
        "success": True,
        "app": {
            "name": "THRONE",
            "version": "1.0",
            "theme": "dark_gold",
        },
        "state": state.data,
        "lobby": lobby_data(),
    }


# ============================================================
# SERIALIZATION
# ============================================================

def serialize(
    result: MiniAppResult,
) -> dict:

    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
    }


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "MiniAppResult",
    "CHARACTERS",
    "CLOTHING",
    "WEAPONS",
    "HORSES",
    "get_character",
    "get_all_characters",
    "choose_character",
    "normalize_level",
    "level_progress",
    "get_world_phase",
    "world_phase_data",
    "st
