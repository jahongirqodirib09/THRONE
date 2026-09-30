import aiosqlite

from config import DATABASE_PATH


class Database:
    """THRONE SQLite ma'lumotlar bazasi."""

    def __init__(self, path: str = DATABASE_PATH):
        self.path = path

    async def connect(self):
        return await aiosqlite.connect(self.path)

    async def init(self):
        async with await self.connect() as db:
            await db.execute("PRAGMA foreign_keys = ON")

            # Foydalanuvchilar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT NOT NULL DEFAULT '',
                    nickname TEXT,
                    language TEXT NOT NULL DEFAULT 'uz',
                    level INTEGER NOT NULL DEFAULT 1,
                    xp INTEGER NOT NULL DEFAULT 0,
                    gold INTEGER NOT NULL DEFAULT 0,
                    coin INTEGER NOT NULL DEFAULT 0,
                    diamond INTEGER NOT NULL DEFAULT 0,
                    elite_pass INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Guruh sozlamalari
            await db.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    group_id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    day_time INTEGER NOT NULL DEFAULT 45,
                    vote_time INTEGER NOT NULL DEFAULT 45,
                    night_time INTEGER NOT NULL DEFAULT 60,
                    start_time INTEGER NOT NULL DEFAULT 30,
                    language TEXT NOT NULL DEFAULT 'uz',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Klanlar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS clans (
                    clan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    leader_id INTEGER NOT NULL,
                    level INTEGER NOT NULL DEFAULT 1,
                    treasury_gold INTEGER NOT NULL DEFAULT 0,
                    treasury_coin INTEGER NOT NULL DEFAULT 0,
                    treasury_diamond INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Klan a'zolari
            await db.execute("""
                CREATE TABLE IF NOT EXISTS clan_members (
                    clan_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    clan_role TEXT NOT NULL DEFAULT 'member',
                    joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (clan_id, user_id),
                    FOREIGN KEY (clan_id) REFERENCES clans(clan_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                )
            """)

            # Juftliklar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS couples (
                    couple_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user1_id, user2_id),
                    FOREIGN KEY (user1_id) REFERENCES users(user_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (user2_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                )
            """)

            # O'yinlar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    phase TEXT NOT NULL DEFAULT 'waiting',
                    day_number INTEGER NOT NULL DEFAULT 0,
                    started_at TEXT,
                    ended_at TEXT,
                    winner TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # O'yin ishtirokchilari
            await db.execute("""
                CREATE TABLE IF NOT EXISTS game_players (
                    game_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role TEXT,
                    side TEXT,
                    alive INTEGER NOT NULL DEFAULT 1,
                    joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    eliminated_at TEXT,
                    PRIMARY KEY (game_id, user_id),
                    FOREIGN KEY (game_id) REFERENCES games(game_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                )
            """)

            # Inventar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    user_id INTEGER NOT NULL,
                    item_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY (user_id, item_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                )
            """)

            # Statistika
            await db.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    user_id INTEGER PRIMARY KEY,
                    games_played INTEGER NOT NULL DEFAULT 0,
                    wins INTEGER NOT NULL DEFAULT 0,
                    losses INTEGER NOT NULL DEFAULT 0,
                    attacks INTEGER NOT NULL DEFAULT 0,
                    kills INTEGER NOT NULL DEFAULT 0,
                    successful_defenses INTEGER NOT NULL DEFAULT 0,
                    successful_investigations INTEGER NOT NULL DEFAULT 0,
                    votes INTEGER NOT NULL DEFAULT 0,
                    tasks_completed INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                )
            """)

            await db.commit()

    async def create_user(
        self,
        user_id: int,
        username: str = "",
        first_name: str = "",
    ):
        async with await self.connect() as db:
            await db.execute(
                """
                INSERT OR IGNORE INTO users
                    (user_id, username, first_name)
                VALUES (?, ?, ?)
                """,
                (user_id, username, first_name),
            )

            await db.execute(
                """
                INSERT OR IGNORE INTO statistics (user_id)
                VALUES (?)
                """,
                (user_id,),
            )

            await db.commit()

    async def get_user(self, user_id: int):
        async with await self.connect() as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,),
            )
            return await cursor.fetchone()

    async def update_user(self, user_id: int, **fields):
        if not fields:
            return

        allowed = {
            "username",
            "first_name",
            "nickname",
            "language",
            "level",
            "xp",
            "gold",
            "coin",
            "diamond",
            "elite_pass",
        }

        invalid = set(fields) - allowed
        if invalid:
            raise ValueError(
                f"Ruxsat etilmagan user maydonlari: {', '.join(sorted(invalid))}"
            )

        assignments = ", ".join(f"{key} = ?" for key in fields)
        values = list(fields.values())
        values.append(user_id)

        async with await self.connect() as db:
            await db.execute(
                f"""
                UPDATE users
                SET {assignments},
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                values,
            )
            await db.commit()

    async def add_xp(self, user_id: int, amount: int):
        if amount < 0:
            raise ValueError("XP manfiy bo'lishi mumkin emas.")

        async with await self.connect() as db:
            await db.execute(
                """
                UPDATE users
                SET xp = xp + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (amount, user_id),
            )
            await db.commit()

    async def change_balance(
        self,
        user_id: int,
        *,
        gold: int = 0,
        coin: int = 0,
        diamond: int = 0,
        allow_negative: bool = False,
    ):
        async with await self.connect() as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute(
                """
                SELECT gold, coin, diamond
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            )
            user = await cursor.fetchone()

            if user is None:
                raise ValueError("Foydalanuvchi topilmadi.")

            new_gold = user["gold"] + gold
            new_coin = user["coin"] + coin
            new_diamond = user["diamond"] + diamond

            if not allow_negative:
                if new_gold < 0 or new_coin < 0 or new_diamond < 0:
                    raise ValueError("Balans yetarli emas.")

            await db.execute(
                """
                UPDATE users
                SET gold = ?,
                    coin = ?,
                    diamond = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (new_gold, new_coin, new_diamond, user_id),
            )

            await db.commit()
