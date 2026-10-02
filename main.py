from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application

from config import BOT_TOKEN
from database import init_db
from handlers import register_handlers


# Telegram va Railway loglari
logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Bot ishga tushishidan oldin bazani tayyorlaydi."""
    await init_db()
    logger.info("THRONE database tayyor.")


async def post_shutdown(application: Application) -> None:
    """Bot to‘xtaganda bajariladi."""
    logger.info("THRONE bot to‘xtadi.")


def build_application() -> Application:
    """Telegram Application obyektini yaratadi."""

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    register_handlers(application)

    return application


def main() -> None:
    """Botni ishga tushiradi."""

    logger.info("THRONE bot ishga tushmoqda...")

    application = build_application()

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
