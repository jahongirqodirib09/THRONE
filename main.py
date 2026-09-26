import asyncio
import logging

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


# ============================================================
# THRONE — MAIN
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
# SET BOT COMMANDS
# ============================================================

async def setup_commands(bot: Bot):
    commands = [
        BotCommand(
            command=command,
            description=description,
        )
        for command, description in COMMANDS
    ]

    await bot.set_my_commands(commands)


# ============================================================
# CREATE BOT
# ============================================================

def create_bot() -> Bot:
    return Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )


# ============================================================
# CREATE DISPATCHER
# ============================================================

def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    # Admin router
    dp.include_router(admin_router)

    # Group game router
    dp.include_router(group_router)

    # Private commands/router
    dp.include_router(private_router)

    # Main handlers
    dp.include_router(handlers_router)

    return dp


# ============================================================
# STARTUP
# ============================================================

async def on_startup(bot: Bot):
    logger.info("THRONE database ishga tushmoqda...")

    await init_db()

    await setup_commands(bot)

    logger.info("THRONE database tayyor.")
    logger.info("THRONE commands o'rnatildi.")
    logger.info("THRONE BOT IS RUNNING...")


# ============================================================
# SHUTDOWN
# ============================================================

async def on_shutdown(bot: Bot):
    logger.info("THRONE BOT to'xtatilmoqda...")

    try:
        await bot.session.close()
    except Exception:
        pass

    logger.info("THRONE BOT to'xtadi.")


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

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("THRONE BOT yopildi.")
