from __future__ import annotations

import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi. Railway Variables bo‘limiga BOT_TOKEN qo‘shing."
    )


DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "throne.db",
).strip() or "throne.db"


MIN_PLAYERS = 4
MAX_PLAYERS = 36

VOTING_SECONDS = 45

DISCUSSION_SECONDS = 45

INACTIVITY_WARNING_SECONDS = 60

INACTIVITY_KICK_SECONDS = 120


GAME_NAME = "THRONE"
GAME_TITLE = "👑 THRONE — Taxtlar O‘yini"


CREATOR_ID_RAW = os.getenv("CREATOR_ID", "").strip()

try:
    CREATOR_ID = int(CREATOR_ID_RAW) if CREATOR_ID_RAW else None
except ValueError as exc:
    raise RuntimeError(
        "CREATOR_ID raqam bo‘lishi kerak."
    ) from exc


def is_creator(user_id: int) -> bool:
    """Foydalanuvchi creator ekanini tekshiradi."""
    return CREATOR_ID is not None and user_id == CREATOR_ID
