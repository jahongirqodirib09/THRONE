import aiosqlite
from typing import Optional

DB_NAME = "throne.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

async def get_db():
    db = await aiosqlite.connect(DB_NAME)
    db.row_factory = aiosqlite.Row
    return db


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

async def init_db():
    db = await get_db()

    await db.executescript("""
    PRAGMA foreign_keys = ON;

    -- ======================================================
    -- USERS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT DEFAULT '',
        full_name TEXT DEFAULT '',
        nickname TEXT DEFAULT '',
        level INTEGER DEFAULT 1,
        experience INTEGER DEFAULT 0,
        gold INTEGER DEFAULT 1000,
        coin INTEGER DEFAULT 0,
        diamond INTEGER DEFAULT 0,
        elite_until TEXT,
        language TEXT DEFAULT 'uz',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- SETTINGS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER PRIMARY KEY,
        notifications INTEGER DEFAULT 1,
        sound INTEGER DEFAULT 1,
        animations INTEGER DEFAULT 1,
        privacy INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    );

    -- ======================================================
    -- PLAYER STATS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS player_stats (
        user_id INTEGER PRIMARY KEY,
        games_played INTEGER DEFAULT 0,
        games_won INTEGER DEFAULT 0,
        games_lost INTEGER DEFAULT 0,
        kills INTEGER DEFAULT 0,
        deaths INTEGER DEFAULT 0,
        ranking_points INTEGER DEFAULT 0,
        duel_wins INTEGER DEFAULT 0,
        duel_losses INTEGER DEFAULT 0,
        tournament_wins INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    );

    -- ======================================================
    -- KINGDOM
    -- ======================================================

    CREATE TABLE IF NOT EXISTS kingdoms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER UNIQUE NOT NULL,
        name TEXT DEFAULT 'THRONE Kingdom',
        flag TEXT DEFAULT '🏴',
        level INTEGER DEFAULT 1,
        population INTEGER DEFAULT 1,
        gold INTEGER DEFAULT 0,
        defense INTEGER DEFAULT 100,
        military_power INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    );

    -- ======================================================
    -- CASTLE
    -- ======================================================

    CREATE TABLE IF NOT EXISTS castles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER UNIQUE NOT NULL,
        level INTEGER DEFAULT 1,
        defense INTEGER DEFAULT 100,
        guards INTEGER DEFAULT 10,
        treasury_capacity INTEGER DEFAULT 10000,
        FOREIGN KEY (owner_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    );

    -- ======================================================
    -- ARMY
    -- ======================================================

    CREATE TABLE IF NOT EXISTS armies (
        owner_id INTEGER PRIMARY KEY,
        soldiers INTEGER DEFAULT 0,
        archers INTEGER DEFAULT 0,
        guards INTEGER DEFAULT 0,
        cavalry INTEGER DEFAULT 0,
        special_units INTEGER DEFAULT 0,
        FOREIGN KEY (owner_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    );

    -- ======================================================
    -- INVENTORY
    -- ======================================================

    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_key TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        UNIQUE(user_id, item_key),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    );

    -- ======================================================
    -- CLANS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS clans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        flag TEXT DEFAULT '🏴',
        description TEXT DEFAULT '',
        leader_id INTEGER NOT NULL,
        level INTEGER DEFAULT 1,
        experience INTEGER DEFAULT 0,
        treasury INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (leader_id) REFERENCES users(user_id)
    );

    CREATE TABLE IF NOT EXISTS clan_members (
        clan_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        clan_role TEXT DEFAULT 'member',
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (clan_id, user_id),
        FOREIGN KEY (clan_id) REFERENCES clans(id)
            ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    );

    -- ======================================================
    -- CLAN WARS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS clan_wars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attacker_clan_id INTEGER NOT NULL,
        defender_clan_id INTEGER NOT NULL,
        status TEXT DEFAULT 'preparation',
        attacker_score INTEGER DEFAULT 0,
        defender_score INTEGER DEFAULT 0,
        winner_clan_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- FAMILY
    -- ======================================================

    CREATE TABLE IF NOT EXISTS families (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER NOT NULL,
        user2_id INTEGER NOT NULL,
        family_level INTEGER DEFAULT 1,
        family_gold INTEGER DEFAULT 0,
        married_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user1_id),
        UNIQUE(user2_id)
    );

    CREATE TABLE IF NOT EXISTS family_proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proposer_id INTEGER NOT NULL,
        target_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- DAILY REWARDS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS daily_rewards (
        user_id INTEGER PRIMARY KEY,
        last_claim TEXT,
        streak INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    );

    -- ======================================================
    -- TRANSFERS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        currency TEXT NOT NULL,
        amount INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- GIFTS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        gift_key TEXT NOT NULL,
        amount INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- MARKET / SHOP
    -- ======================================================

    CREATE TABLE IF NOT EXISTS market_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_key TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        price_gold INTEGER DEFAULT 0,
        price_coin INTEGER DEFAULT 0,
        price_diamond INTEGER DEFAULT 0,
        quantity INTEGER DEFAULT -1,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_key TEXT NOT NULL,
        currency TEXT NOT NULL,
        price INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS black_market (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_key TEXT NOT NULL,
        price_gold INTEGER DEFAULT 0,
        price_coin INTEGER DEFAULT 0,
        price_diamond INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1
    );

    -- ======================================================
    -- ELITE
    -- ======================================================

    CREATE TABLE IF NOT EXISTS elite_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan TEXT NOT NULL,
        price REAL DEFAULT 0,
        duration_days INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- GROUP GAMES
    -- ======================================================

    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        creator_id INTEGER NOT NULL,
        status TEXT DEFAULT 'lobby',
        phase TEXT DEFAULT 'lobby',
        round_number INTEGER DEFAULT 0,
        min_players INTEGER DEFAULT 7,
        max_players INTEGER DEFAULT 35,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        started_at TEXT,
        ended_at TEXT
    );

    CREATE TABLE IF NOT EXISTS game_players (
        game_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role_key TEXT,
        side TEXT,
        alive INTEGER DEFAULT 1,
        eliminated INTEGER DEFAULT 0,
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (game_id, user_id),
        FOREIGN KEY (game_id) REFERENCES games(id)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS game_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL,
        actor_id INTEGER NOT NULL,
        target_id INTEGER,
        action_type TEXT NOT NULL,
        value TEXT DEFAULT '',
        round_number INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS game_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL,
        voter_id INTEGER NOT NULL,
        target_id INTEGER NOT NULL,
        round_number INTEGER DEFAULT 0,
        UNIQUE(game_id, voter_id, round_number)
    );

    CREATE TABLE IF NOT EXISTS game_results (
        game_id INTEGER PRIMARY KEY,
        winning_side TEXT NOT NULL,
        winner_user_id INTEGER,
        result_text TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- DUELS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS duels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        challenger_id INTEGER NOT NULL,
        opponent_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        winner_id INTEGER,
        stake_type TEXT DEFAULT '',
        stake_amount INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        finished_at TEXT
    );

    -- ======================================================
    -- TOURNAMENTS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS tournaments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tournament_type TEXT DEFAULT 'solo',
        status TEXT DEFAULT 'registration',
        max_players INTEGER DEFAULT 32,
        winner_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        started_at TEXT,
        ended_at TEXT
    );

    CREATE TABLE IF NOT EXISTS tournament_players (
        tournament_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        eliminated INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        PRIMARY KEY (tournament_id, user_id)
    );

    -- ======================================================
    -- RANKING
    -- ======================================================

    CREATE TABLE IF NOT EXISTS ranking_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        points INTEGER NOT NULL,
        reason TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- ROYAL POSITIONS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS royal_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kingdom_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        position TEXT NOT NULL,
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- TERRITORIES
    -- ======================================================

    CREATE TABLE IF NOT EXISTS territories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kingdom_id INTEGER,
        name TEXT UNIQUE NOT NULL,
        income INTEGER DEFAULT 0,
        strategic_value INTEGER DEFAULT 0,
        defense_requirement INTEGER DEFAULT 0,
        controlled INTEGER DEFAULT 0
    );

    -- ======================================================
    -- CHANNEL POSTS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS channel_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id INTEGER NOT NULL,
        message_id INTEGER,
        post_type TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- SECURITY
    -- ======================================================

    CREATE TABLE IF NOT EXISTS security_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- CHAT SETTINGS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS chat_settings (
        chat_id INTEGER PRIMARY KEY,
        language TEXT DEFAULT 'uz',
        game_enabled INTEGER DEFAULT 1,
        admin_only_start INTEGER DEFAULT 1,
        welcome_enabled INTEGER DEFAULT 1
    );

    -- ======================================================
    -- MINI APP
    -- ======================================================

    CREATE TABLE IF NOT EXISTS mini_profiles (
        user_id INTEGER PRIMARY KEY,
        character_key TEXT,
        background_key TEXT,
        clothing_key TEXT,
        weapon_key TEXT,
        horse_key TEXT,
        level INTEGER DEFAULT 1,
        experience INTEGER DEFAULT 0,
        character_locked INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS friends (
        user_id INTEGER NOT NULL,
        friend_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, friend_id)
    );

    CREATE TABLE IF NOT EXISTS inactivity (
        user_id INTEGER PRIMARY KEY,
        last_activity TEXT DEFAULT CURRENT_TIMESTAMP,
        warning_sent INTEGER DEFAULT 0,
        removed INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    );

    -- ======================================================
    -- AI LOG
    -- ======================================================

    CREATE TABLE IF NOT EXISTS ai_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- ======================================================
    -- SYSTEM
    -- ======================================================

    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT DEFAULT ''
    );

    -- ======================================================
    -- INDEXES
    -- ======================================================

    CREATE INDEX IF NOT EXISTS idx_game_players_game
        ON game_players(game_id);

    CREATE INDEX IF NOT EXISTS idx_game_actions_game
        ON game_actions(game_id);

    CREATE INDEX IF NOT EXISTS idx_game_votes_game
        ON game_votes(game_id);

    CREATE INDEX IF NOT EXISTS idx_clan_members_clan
        ON clan_members(clan_id);

    CREATE INDEX IF NOT EXISTS idx_ranking_points
        ON player_stats(ranking_points DESC);

    CREATE INDEX IF NOT EXISTS idx_security_user
        ON security_logs(user_id);

    """)

    await db.commit()
    await db.close()


# ============================================================
# BASIC DATABASE HELPERS
# ============================================================

async def fetchone(query: str, params=()):
    db = await get_db()

    try:
        cursor = await db.execute(query, params)
        row = await cursor.fetchone()
        await cursor.close()
        return row
    finally:
        await db.close()


async def fetchall(query: str, params=()):
    db = await get_db()

    try:
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        await cursor.close()
        return rows
    finally:
        await db.close()


async def execute(query: str, params=()):
    db = await get_db()

    try:
        cursor = await db.execute(query, params)
        await db.commit()
        last_id = cursor.lastrowid
        await cursor.close()
        return last_id
    finally:
        await db.close()


# ============================================================
# USER FUNCTIONS
# ============================================================

async def get_user(user_id: int):
    return await fetchone(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    )


async def create_user(
    user_id: int,
    username: str = "",
    full_name: str = ""
):
    await execute("""
        INSERT OR IGNORE INTO users
        (user_id, username, full_name)
        VALUES (?, ?, ?)
    """, (user_id, username, full_name))

    await execute("""
        INSERT OR IGNORE INTO settings
        (user_id)
        VALUES (?)
    """, (user_id,))

    await execute("""
        INSERT OR IGNORE INTO player_stats
        (user_id)
        VALUES (?)
    """, (user_id,))

    await execute("""
        INSERT OR IGNORE INTO mini_profiles
        (user_id)
        VALUES (?)
    """, (user_id,))

    await execute("""
        INSERT OR IGNORE INTO inactivity
        (user_id)
        VALUES (?)
    """, (user_id,))


async def update_user_info(
    user_id: int,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
    nickname: Optional[str] = None,
    language: Optional[str] = None
):
    await execute("""
        UPDATE users
        SET username = COALESCE(?, usernam
