import os

from dotenv import load_dotenv

load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Required environment variable is missing: {name}"
        )

    return value


def get_int_env(name: str, default: int = 0) -> int:
    value = os.getenv(name)

    if value is None or value.strip() == "":
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable {name} must be an integer."
        ) from exc


# ---------------------------------------------------------
# Telegram
# ---------------------------------------------------------

BOT_TOKEN = get_required_env("BOT_TOKEN")

# Creator / owner Telegram user ID
CREATOR_ID = get_int_env("CREATOR_ID")


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

# database.py shu bilan bir xil nomni o'qiydi: DATABASE_PATH
DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "throne.db",
)


# ---------------------------------------------------------
# Mini App / Web
# ---------------------------------------------------------

WEBAPP_URL = os.getenv(
    "WEBAPP_URL",
    "",
).rstrip("/")


HOST = os.getenv(
    "HOST",
    "0.0.0.0",
)

PORT = get_int_env(
    "PORT",
    10000,
)


# ---------------------------------------------------------
# Official THRONE channel
# ---------------------------------------------------------

CHANNEL_ID = os.getenv(
    "CHANNEL_ID",
    "",
)


# ---------------------------------------------------------
# Payments
# ---------------------------------------------------------

PAYMENT_PROVIDER_TOKEN = os.getenv(
    "PAYMENT_PROVIDER_TOKEN",
    "",
)


# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

APP_NAME = "THRONE"

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0",
)


# ---------------------------------------------------------
# Game limits
# ---------------------------------------------------------

MIN_PLAYERS = 7
MAX_PLAYERS = 35

LAST_WORDS_SECONDS = 30


# ---------------------------------------------------------
# Elite
# ---------------------------------------------------------

ELITE_7_DAYS_DIAMONDS = 20
ELITE_15_DAYS_DIAMONDS = 0
ELITE_30_DAYS_DIAMONDS = 200
ELITE_90_DAYS_DIAMONDS = 650
ELITE_180_DAYS_DIAMONDS = 1200
ELITE_365_DAYS_DIAMONDS = 2300


# ---------------------------------------------------------
# Security
# ---------------------------------------------------------

MAX_CALLBACK_AGE_SECONDS = 300

RATE_LIMIT_ENABLED = True


def is_creator(user_id: int) -> bool:
    """
    Returns True only for the configured creator account.
    """
    return user_id == CREATOR_ID


def validate_config() -> None:
    """
    Validates the most important production settings.
    """
    if CREATOR_ID <= 0:
        raise RuntimeError(
            "CREATOR_ID must be a valid Telegram user ID."
        )

    if PORT <= 0 or PORT > 65535:
        raise RuntimeError(
            "PORT must be between 1 and 65535."
        )

    if MIN_PLAYERS < 2:
        raise RuntimeError(
            "MIN_PLAYERS must be at least 2."
        )

    if MAX_PLAYERS < MIN_PLAYERS:
        raise RuntimeError(
            "MAX_PLAYERS must be greater than or equal to MIN_PLAYERS."
        )
        
