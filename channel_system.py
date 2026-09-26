# ============================================================
# THRONE — CHANNEL SYSTEM
# ============================================================

from dataclasses import dataclass
from typing import Optional, Any

from config import CREATOR_ID
from database import (
    get_top_players,
    fetchall,
    execute,
)


# ============================================================
# CONSTANTS
# ============================================================

POST_RANKING = "ranking"
POST_CLAN_RANKING = "clan_ranking"
POST_TOURNAMENT = "tournament"
POST_ANNOUNCEMENT = "announcement"
POST_REWARD = "reward"
POST_EVENT = "event"
POST_SYSTEM = "system"

DEFAULT_LIMIT = 10
MAX_LIMIT = 50


# ============================================================
# RESULT
# ============================================================

@dataclass
class ChannelResult:
    success: bool
    message: str
    data: Optional[dict] = None


# ============================================================
# CREATOR
# ============================================================

def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


# ============================================================
# CHANNEL CONFIG
# ============================================================

@dataclass
class ChannelConfig:
    channel_id: int
    enabled: bool = True
    auto_ranking: bool = True
    auto_clan_ranking: bool = True
    auto_tournament: bool = True
    auto_rewards: bool = True
    auto_events: bool = True


# ============================================================
# LIMIT
# ============================================================

def normalize_limit(limit: int) -> int:
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT

    return max(
        1,
        min(
            MAX_LIMIT,
            limit,
        ),
    )


# ============================================================
# USER RANKING
# ============================================================

async def get_player_ranking(
    limit: int = DEFAULT_LIMIT,
) -> list:

    limit = normalize_limit(limit)

    try:
        players = await get_top_players(
            limit
        )
    except TypeError:
        players = await get_top_players()

    if not players:
        return []

    return list(players)[:limit]


# ============================================================
# PLAYER NAME
# ============================================================

def player_name(
    player: Any,
    position: int,
) -> str:

    if not isinstance(
        player,
        dict,
    ):
        return f"{position}-o‘rin"

    name = (
        player.get("first_name")
        or player.get("username")
        or player.get("name")
        or f"O‘yinchi #{position}"
    )

    return str(name)


# ============================================================
# RANKING TEXT
# ============================================================

async def build_ranking_post(
    limit: int = DEFAULT_LIMIT,
) -> str:

    players = await get_player_ranking(
        limit
    )

    lines = [
        "👑 THRONE — REYTING",
        "",
        "🏆 Qirollikning eng kuchli o‘yinchilari:",
        "",
    ]

    if not players:
        lines.append(
            "Hozircha reyting ma’lumotlari mavjud emas."
        )
        return "\n".join(lines)

    medals = {
        1: "🥇",
        2: "🥈",
        3: "🥉",
    }

    for index, player in enumerate(
        players,
        start=1,
    ):

        medal = medals.get(
            index,
            f"{index}.",
        )

        name = player_name(
            player,
            index,
        )

        points = (
            player.get(
                "ranking_points",
                player.get(
                    "points",
                    0,
                ),
            )
            if isinstance(
                player,
                dict,
            )
            else 0
        )

        level = (
            player.get(
                "level",
                1,
            )
            if isinstance(
                player,
                dict,
            )
            else 1
        )

        lines.append(
            f"{medal} {name} — "
            f"⭐ {points} | "
            f"LVL {level}"
        )

    lines.extend(
        [
            "",
            "⚜️ THRONE — Har bir g‘alaba tarixga aylanadi.",
        ]
    )

    return "\n".join(lines)


# ============================================================
# CLAN RANKING
# ============================================================

async def get_clan_ranking(
    limit: int = DEFAULT_LIMIT,
) -> list:

    limit = normalize_limit(limit)

    try:
        rows = await fetchall(
            """
            SELECT
                id,
                name,
                flag,
                level,
                power,
                ranking_points
            FROM clans
            ORDER BY ranking_points DESC,
                     power DESC,
                     level DESC
            LIMIT ?
            """,
            (limit,),
        )

        return rows or []

    except Exception:
        return []


# ============================================================
# CLAN RANKING POST
# ============================================================

async def build_clan_ranking_post(
    limit: int = DEFAULT_LIMIT,
) -> str:

    clans = await get_clan_ranking(
        limit
    )

    lines = [
        "🏴 THRONE — KLANLAR REYTINGI",
        "",
        "⚔️ Qirollikdagi eng kuchli klanlar:",
        "",
    ]

    if not clans:
        lines.append(
            "Hozircha klan reytingi mavjud emas."
        )
        return "\n".join(lines)

    medals = {
        1: "🥇",
        2: "🥈",
        3: "🥉",
    }

    for index, clan in enumerate(
        clans,
        start=1,
    ):

        if not isinstance(
            clan,
            dict,
        ):
            continue

        medal = medals.get(
            index,
            f"{index}.",
        )

        flag = clan.get(
            "flag",
            "🏴",
        )

        name = clan.get(
            "name",
            "Noma’lum klan",
        )

        points = clan.get(
            "ranking_points",
            0,
        )

        power = clan.get(
            "power",
            0,
        )

        level = clan.get(
            "level",
            1,
        )

        lines.append(
            f"{medal} {flag} {name}\n"
            f"   ⭐ {points} | "
            f"⚔️ {power} | "
            f"LVL {level}"
        )

    lines.extend(
        [
            "",
            "👑 THRONE — Kuch birlikda.",
        ]
    )

    return "\n".join(lines)


# ============================================================
# TOURNAMENT POST
# ============================================================

def build_tournament_post(
    tournament_name: str,
    winner_name: str,
    tournament_type: str = "THRONE CUP",
    reward: Optional[str] = None,
) -> str:

    lines = [
        "🏆 THRONE — MUSOBAQA NATIJASI",
        "",
        f"⚔️ {tournament_name}",
        f"🏟️ {tournament_type}",
        "",
        "👑 G‘OLIB:",
        f"🥇 {winner_name}",
    ]

    if reward:
        lines.extend(
            [
                "",
                f"🎁 Mukofot: {reward}",
            ]
        )

    lines.extend(
        [
            "",
            "⚜️ Yangi janglar hali oldinda.",
        ]
    )

    return "\n".join(lines)


# ============================================================
# REWARD POST
# ============================================================

def build_reward_post(
    title: str,
    description: str,
    reward: str,
) -> str:

    return "\n".join(
        [
            "🎁 THRONE — MUKOFOT",
            "",
            f"👑 {title}",
            "",
            description,
            "",
            f"💎 Mukofot: {reward}",
            "",
            "⚜️ THRONE qirolligida mukofotlar davom etadi.",
        ]
    )


# ============================================================
# EVENT POST
# ============================================================

def build_event_post(
    title: str,
    description: str,
    start_text: Optional[str] = None,
    reward: Optional[str] = None,
) -> str:

    lines = [
        "🔥 THRONE — YANGI VOQEA",
        "",
        f"👑 {title}",
        "",
        description,
    ]

    if start_text:
        lines.extend(
            [
                "",
                f"🕐 Boshlanishi: {start_text}",
            ]
        )

    if reward:
        lines.extend(
            [
                "",
                f"🎁 Mukofot: {reward}",
            ]
        )

    lines.extend(
        [
            "",
            "⚔️ Qirollik seni kutmoqda.",
        ]
    )

    return "\n".join(lines)


# ============================================================
# ANNOUNCEMENT
# ============================================================

def build_announcement(
    title: str,
    text: str,
) -> str:

    return "\n".join(
        [
            "📢 THRONE — E’LON",
            "",
            f"👑 {title}",
            "",
            text,
            "",
            "⚜️ THRONE",
        ]
    )


# ============================================================
# SYSTEM POST
# ============================================================

def build_system_post(
    title: str,
    text: str,
) -> str:

    return "\n".join(
        [
            "⚙️ THRONE — TIZIM",
            "",
            f"👑 {title}",
            "",
            text,
        ]
    )


# ============================================================
# CHANNEL POST RECORD
# ============================================================

async def save_channel_post(
    channel_id: int,
    post_type: str,
    text: str,
) -> ChannelResult:

    if not text.strip():
        return ChannelResult(
            False,
            "❌ Post matni bo‘sh.",
        )

    try:

        result = await execute(
            """
            INSERT INTO channel_posts
            (
                channel_id,
                post_type,
                text
            )
            VALUES (?, ?, ?)
            """,
            (
                channel_id,
                post_type,
                text,
            ),
        )

        return ChannelResult(
            True,
            "✅ Kanal posti saqlandi.",
            {
                "result": result,
            },
        )

    except Exception as exc:

        return ChannelResult(
            False,
            "❌ Kanal posti saqlanmadi.",
            {
                "error": str(exc),
            },
        )


# ============================================================
# RECENT POSTS
# ============================================================

async def get_recent_posts(
    channel_id: int,
    limit: int = 20,
) -> list:

    limit = normalize_limit(
        min(
            limit,
            20,
        )
    )

    try:

        rows = await fetchall(
            """
            SELECT *
            FROM channel_posts
            WHERE channel_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                channel_id,
                limit,
            ),
        )

        return rows or []

    except Exception:
        return []


# ============================================================
# CHANNEL STATUS
# ============================================================

def channel_status_text(
    config: ChannelConfig,
) -> str:

    return "\n".join(
        [
            "📡 THRONE CHANNEL",
            "",
            f"🆔 Channel: {config.channel_id}",
            f"📢 Avtopost: "
            f"{'ON' if config.enabled else 'OFF'}",
            f"🏆 Reyting: "
            f"{'ON' if config.auto_ranking else 'OFF'}",
            f"🏴 Klan reytingi: "
            f"{'ON' if config.auto_clan_ranking else 'OFF'}",
            f"🏆 Turnir: "
            f"{'ON' if config.auto_tournament else 'OFF'}",
            f"🎁 Mukofot: "
            f"{'ON' if config.auto_rewards else 'OFF'}",
            f"🔥 Event: "
            f"{'ON' if config.auto_events else 'OFF'}",
        ]
    )


# ============================================================
# CHANNEL CONFIGURATION
# ============================================================

def create_channel_config(
    channel_id: int,
) -> ChannelConfig:

    return ChannelConfig(
        channel_id=int(channel_id),
        enabled=True,
        auto_ranking=True,
        auto_clan_ranking=True,
        auto_tournament=True,
        auto_rewards=True,
        auto_events=True,
    )


def toggle_channel(
    config: ChannelConfig,
    enabled: bool,
) -> ChannelConfig:

    config.enabled = bool(
        enabled
    )

    return config


# ============================================================
# POST TYPE CHECK
# ============================================================

VALID_POST_TYPES = {
    POST_RANKING,
    POST_CLAN_RANKING,
    POST_TOURNAMENT,
    POST_ANNOUNCEMENT,
    POST_REWARD,
    POST_EVENT,
    POST_SYSTEM,
}


def valid_post_type(
    post_type: str,
) -> bool:

    return post_type in VALID_POST_TYPES


# ============================================================
# GENERIC POST
# ============================================================

async def create_channel_post(
    channel_id: int,
    post_type: str,
    text: str,
) -> ChannelResult:

    if not valid_post_type(
        post_type
    ):
        return ChannelResult(
            False,
            "❌ Noto‘g‘ri post turi.",
        )

    return await save_channel_post(
        channel_id,
        post_type,
        text,
    )


# ============================================================
# WEEKLY RANKING
# ============================================================

async def weekly_ranking(
    channel_id: int,
    limit: int = 10,
) -> ChannelResult:

    text = await build_ranking_post(
        limit
    )

    return await create_channel_post(
        channel_id,
        POST_RANKING,
        text,
    )


# ============================================================
# CLAN RANKING
# ============================================================

async def weekly_clan_ranking(
    channel_id: int,
    limit: int = 10,
) -> ChannelResult:

    text = await build_clan_ranking_post(
        limit
    )

    return await create_channel_post(
        channel_id,
        POST_CLAN_RANKING,
        text,
    )


# ============================================================
# TOURNAMENT RESULT
# ============================================================

async def tournament_result(
    channel_id: int,
    tournament_name: str,
    winner_name: str,
    tournament_type: str = "THRONE CUP",
    reward: Optional[str] = None,
) -> ChannelResult:

    text = build_tournament_post(
        tournament_name,
        winner_name,
        tournament_type,
        reward,
    )

    return await create_channel_post(
        channel_id,
        POST_TOURNAMENT,
        text,
    )


# ============================================================
# REWARD ANNOUNCEMENT
# ============================================================

async def reward_announcement(
    channel_id: int,
    title: str,
    description: str,
    reward: str,
) -> ChannelResult:

    text = build_reward_post(
        title,
        description,
        reward,
    )

    return await create_channel_post(
        channel_id,
        POST_REWARD,
        text,
    )


# ============================================================
# EVENT ANNOUNCEMENT
# ============================================================

async def event_announcement(
    channel_id: int,
    title: str,
    description: str,
    start_text: Optional[str] = None,
    reward: Optional[str] = None,
) -> ChannelResult:

    text = build_event_post(
        title,
        description,
        start_text,
        reward,
    )

    return await create_channel_post(
        channel_id,
        POST_EVENT,
        text,
    )


# ============================================================
# ADMIN CHECK
# ============================================================

def can_manage_channel(
    user_id: int,
) -> bool:

    return is_creator(
        user_id
    )


# ============================================================
# SERIALIZE
# ============================================================

def serialize_config(
    config: ChannelConfig,
) -> dict:

    return {
        "channel_id": config.channel_id,
        "enabled": config.enabled,
        "auto_ranking": config.auto_ranking,
        "auto_clan_ranking": config.auto_clan_ranking,
        "auto_tournament": config.auto_tournament,
        "auto_rewards": config.auto_rewards,
        "auto_events": config.auto_events,
    }


# ============================================================
# CHANNEL DASHBOARD
# ============================================================

def channel_dashboard(
    config: ChannelConfig,
) -> dict:

    return {
        "channel": serialize_config(
            config
        ),
        "supported_posts": list(
            VALID_POST_TYPES
        ),
        "limits": {
            "ranking": MAX_LIMIT,
            "recent_posts": 20,
        },
    }


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "ChannelResult",
    "ChannelConfig",
    "POST_RANKING",
    "POST_CLAN_RANKING",
    "POST_TOURNAMENT",
    "POST_ANNOUNCEMENT",
    "POST_REWARD",
    "POST_EVENT",
    "POST_SYSTEM",
    "is_creator",
    "get_player_ranking",
    "build_ranking_post",
    "get_clan_ranking",
    "build_clan_ranking_post",
    "build_tournament_post",
    "build_reward_post",
    "build_event_post",
    "build_announcement",
    "build_system_post",
    "save_channel_post",
    "get_recent_posts",
    "channel_status_text",
    "create_channel_config",
    "toggle_channel",
    "create_channel_post",
    "weekly_ranking",
    "weekly_clan_ranking",
    "tournament_result",
    "reward_announcement",
    "event_announcement",
    "can_manage_channel",
    "serialize_config",
    "channel_dashboard",
  ]
