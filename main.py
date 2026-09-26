import asyncio
import logging
import os

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import init_db

from handlers import router as handlers_router
from group_handlers import router as group_router
from private_handlers import router as private_router
from admin_handlers import router as admin_router

from webapp_server import create_app


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("THRONE")


# ============================================================
# BOT COMMANDS
# ============================================================

COMMANDS = [
    ("start", "THRONE'ni ishga tushirish"),
    ("help", "Yordam"),
    ("rules", "Qoidalar"),
    ("profile", "Profil"),
    ("inventory", "Inventar"),
    ("wallet", "Hamyon"),
    ("gold", "Oltin"),
    ("coin", "Coin"),
    ("diamond", "Olmos"),
    ("daily", "Kunlik bonus"),
    ("kingdom", "Qirollik"),
    ("castle", "Qal'a"),
    ("throne", "Taxt"),
    ("army", "Qo'shin"),
    ("clan", "Klan"),
    ("clans", "Klanlar"),
    ("clanwar", "Klan urushi"),
    ("map", "Xarita"),
    ("territory", "Hudud"),
    ("wars", "Urushlar"),
    ("market", "Bozor"),
    ("shop", "Do'kon"),
    ("transfer", "Oltin o'tkazish"),
    ("gift", "Sovg'a"),
    ("ranking", "Reyting"),
    ("clanranking", "Klan reytingi"),
    ("stats", "Statistika"),
    ("settings", "Sozlamalar"),
]


# ============================================================
# BOT
# ============================================================

def create_bot() -> Bot:
    return Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        ),
    )


def create_dispatcher() -> Dispatcher:

    dp = Dispatcher()

    dp.include_router(admin_router)
    dp.include_router(group_router)
    dp.include_router(private_router)
    dp.include_router(handlers_router)

    return dp


# ============================================================
# COMMAND SETUP
# ============================================================

async def setup_commands(bot: Bot):

    commands = [
        BotCommand(
            command=command,
            description=description
        )
        for command, description in COMMANDS
    ]

    await bot.set_my_commands(commands)


# ============================================================
# STARTUP
# ============================================================

async def on_startup(bot: Bot):

    logger.info(
        "THRONE database ishga tushmoqda..."
    )

    await init_db()

    await setup_commands(bot)

    logger.info(
        "THRONE database tayyor."
    )

    logger.info(
        "THRONE commands o'rnatildi."
    )

    logger.info(
        "THRONE BOT IS RUNNING..."
    )


# ============================================================
# WEB SERVER
# ============================================================

async def start_web_server():

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )

    app = create_app()

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=port
    )

    await site.start()

    logger.info(
        "THRONE Mini App API running on port %s",
        port
    )

    return runner


# ============================================================
# MAIN
# ============================================================

async def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN topilmadi. "
            "Hosting Environment Variables ichiga BOT_TOKEN qo'ying."
        )


    bot = create_bot()

    dp = create_dispatcher()


    await on_startup(
        bot
    )


    web_runner = None


    try:

        # Mini App API server
        web_runner = await start_web_server()


        # Telegram bot
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )


    finally:

        if web_runner:

            await web_runner.cleanup()


        try:

            await bot.session.close()

        except Exception:

            pass


        logger.info(
            "THRONE BOT to'xtadi."
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except (
        KeyboardInterrupt,
        SystemExit
    ):

        logger.info(
            "THRONE BOT yopildi."
    )
