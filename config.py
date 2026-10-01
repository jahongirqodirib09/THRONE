import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi. Railway Variables ichiga BOT_TOKEN qo‘shing.")

# THRONE asosiy sozlamalari
GAME_NAME = "THRONE"
GAME_TITLE = "Taxtlar O‘yini 👑⚔️"

# Standart vaqtlar
DEFAULT_DAY_TIME = 45
DEFAULT_VOTE_TIME = 45
DEFAULT_NIGHT_TIME = 60
DEFAULT_GAME_START_TIME = 30

# O‘yin chegaralari
MIN_PLAYERS = 4
MAX_PLAYERS = 50

# Ma'lumotlar bazasi
DATABASE_PATH = os.getenv("DATABASE_PATH", "throne.db")

# Creator
CREATOR_ID = int(os.getenv("CREATOR_ID", "0"))

# WebApp
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()
