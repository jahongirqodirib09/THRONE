import aiosqlite

from config import DATABASE_PATH


# ============================================================
# DATABASE CONNECTION
# ============================================================

async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DATABASE_PATH)

    db.row_factory = aiosqlite.Row

    await db.execute("PRAGMA foreign_keys = ON")
    await db.execute("PRAGMA journal_mode = WAL")
    await db.execute("PRAGMA busy_timeout = 5000")

    return db


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

async def init_db() -> None:
    db = await get_db()

    try:
        await db.executescript(
            """
            PRAGMA foreign_keys = ON;

            -- ==================================================
            -- USERS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,

                language TEXT NOT NULL DEFAULT 'uz',

                gold INTEGER NOT NULL DEFAULT 0,
                coin INTEGER NOT NULL DEFAULT 0,
                diamond INTEGER NOT NULL DEFAULT 0,

                level INTEGER NOT NULL DEFAULT 1,
                experience INTEGER NOT NULL DEFAULT 0,
                power INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_active_at TEXT,

                is_banned INTEGER NOT NULL DEFAULT 0,
                is_creator INTEGER NOT NULL DEFAULT 0
            );


            -- ==================================================
            -- SETTINGS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER PRIMARY KEY,

                language TEXT NOT NULL DEFAULT 'uz',
                notifications INTEGER NOT NULL DEFAULT 1,
                animations INTEGER NOT NULL DEFAULT 1,
                performance_mode TEXT NOT NULL DEFAULT 'full',

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- PLAYER STATS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS player_stats (
                user_id INTEGER PRIMARY KEY,

                games_played INTEGER NOT NULL DEFAULT 0,
                games_won INTEGER NOT NULL DEFAULT 0,
                games_lost INTEGER NOT NULL DEFAULT 0,

                duels_played INTEGER NOT NULL DEFAULT 0,
                duels_won INTEGER NOT NULL DEFAULT 0,
                duels_lost INTEGER NOT NULL DEFAULT 0,

                tournaments_played INTEGER NOT NULL DEFAULT 0,
                tournaments_won INTEGER NOT NULL DEFAULT 0,

                ranking_points INTEGER NOT NULL DEFAULT 0,
                win_streak INTEGER NOT NULL DEFAULT 0,
                best_win_streak INTEGER NOT NULL DEFAULT 0,

                total_gold_earned INTEGER NOT NULL DEFAULT 0,
                total_coin_earned INTEGER NOT NULL DEFAULT 0,
                total_diamond_earned INTEGER NOT NULL DEFAULT 0,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- KINGDOMS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS kingdoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                owner_id INTEGER NOT NULL UNIQUE,

                name TEXT NOT NULL DEFAULT 'Yangi Qirollik',
                flag TEXT NOT NULL DEFAULT 'royal',

                level INTEGER NOT NULL DEFAULT 1,
                population INTEGER NOT NULL DEFAULT 0,

                gold INTEGER NOT NULL DEFAULT 0,
                defense INTEGER NOT NULL DEFAULT 0,
                military_power INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (owner_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- CASTLES
            -- ==================================================

            CREATE TABLE IF NOT EXISTS castles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                kingdom_id INTEGER NOT NULL UNIQUE,

                name TEXT NOT NULL DEFAULT 'Qirollik Qal’asi',
                level INTEGER NOT NULL DEFAULT 1,

                defense INTEGER NOT NULL DEFAULT 0,
                guards INTEGER NOT NULL DEFAULT 0,
                treasury_capacity INTEGER NOT NULL DEFAULT 10000,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (kingdom_id)
                    REFERENCES kingdoms(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- ARMIES
            -- ==================================================

            CREATE TABLE IF NOT EXISTS armies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                kingdom_id INTEGER NOT NULL UNIQUE,

                soldiers INTEGER NOT NULL DEFAULT 0,
                archers INTEGER NOT NULL DEFAULT 0,
                guards INTEGER NOT NULL DEFAULT 0,
                cavalry INTEGER NOT NULL DEFAULT 0,
                special_units INTEGER NOT NULL DEFAULT 0,

                attack INTEGER NOT NULL DEFAULT 0,
                defense INTEGER NOT NULL DEFAULT 0,

                FOREIGN KEY (kingdom_id)
                    REFERENCES kingdoms(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- INVENTORY
            -- ==================================================

            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                item_name TEXT NOT NULL,

                category TEXT NOT NULL DEFAULT 'special',

                quantity INTEGER NOT NULL DEFAULT 1,

                attack INTEGER NOT NULL DEFAULT 0,
                defense INTEGER NOT NULL DEFAULT 0,

                equipped INTEGER NOT NULL DEFAULT 0,

                acquired_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(user_id, item_id),

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- CLANS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL DEFAULT '',

                owner_id INTEGER NOT NULL,

                avatar TEXT NOT NULL DEFAULT '',
                frame_id TEXT NOT NULL DEFAULT 'default',
                flag TEXT NOT NULL DEFAULT 'royal',

                level INTEGER NOT NULL DEFAULT 1,
                experience INTEGER NOT NULL DEFAULT 0,
                power INTEGER NOT NULL DEFAULT 0,

                member_limit INTEGER NOT NULL DEFAULT 10,

                treasury INTEGER NOT NULL DEFAULT 0,
                treasury_capacity INTEGER NOT NULL DEFAULT 10000,

                territory_limit INTEGER NOT NULL DEFAULT 1,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (owner_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- CLAN MEMBERS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS clan_members (
                clan_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,

                position TEXT NOT NULL DEFAULT 'member',

                joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (clan_id, user_id),

                FOREIGN KEY (clan_id)
                    REFERENCES clans(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- CLAN WARS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS clan_wars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                attacker_clan_id INTEGER NOT NULL,
                defender_clan_id INTEGER NOT NULL,

                status TEXT NOT NULL DEFAULT 'preparation',

                attacker_score INTEGER NOT NULL DEFAULT 0,
                defender_score INTEGER NOT NULL DEFAULT 0,

                started_at TEXT,
                ended_at TEXT,

                winner_clan_id INTEGER,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (attacker_clan_id)
                    REFERENCES clans(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (defender_clan_id)
                    REFERENCES clans(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- FAMILIES / COUPLES
            -- ==================================================

            CREATE TABLE IF NOT EXISTS families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,

                status TEXT NOT NULL DEFAULT 'active',

                married_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(user1_id, user2_id),

                FOREIGN KEY (user1_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user2_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- FAMILY PROPOSALS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS family_proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,

                status TEXT NOT NULL DEFAULT 'pending',

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                responded_at TEXT,

                FOREIGN KEY (sender_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (receiver_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- DAILY REWARDS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS daily_rewards (
                user_id INTEGER PRIMARY KEY,

                streak INTEGER NOT NULL DEFAULT 0,
                last_claim_at TEXT,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- TRANSFERS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,

                currency TEXT NOT NULL,
                amount INTEGER NOT NULL,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (sender_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (receiver_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- GIFTS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS gifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,

                gift_id TEXT NOT NULL,
                gift_name TEXT NOT NULL,

                quantity INTEGER NOT NULL DEFAULT 1,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (sender_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (receiver_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- MARKET ITEMS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS market_items (
                id TEXT PRIMARY KEY,

                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',

                category TEXT NOT NULL,

                price INTEGER NOT NULL DEFAULT 0,
                currency TEXT NOT NULL DEFAULT 'gold',

                attack INTEGER NOT NULL DEFAULT 0,
                defense INTEGER NOT NULL DEFAULT 0,

                stock INTEGER,

                active INTEGER NOT NULL DEFAULT 1
            );


            -- ==================================================
            -- PURCHASES
            -- ==================================================

            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,

                price INTEGER NOT NULL,
                currency TEXT NOT NULL,

                quantity INTEGER NOT NULL DEFAULT 1,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- BLACK MARKET
            -- ==================================================

            CREATE TABLE IF NOT EXISTS black_market (
                id TEXT PRIMARY KEY,

                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',

                price INTEGER NOT NULL,
                currency TEXT NOT NULL DEFAULT 'gold',

                stock INTEGER NOT NULL DEFAULT 0,

                attack INTEGER NOT NULL DEFAULT 0,
                defense INTEGER NOT NULL DEFAULT 0,

                active INTEGER NOT NULL DEFAULT 1,

                expires_at TEXT
            );


            -- ==================================================
            -- ELITE
            -- ==================================================

            CREATE TABLE IF NOT EXISTS elite_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                duration_days INTEGER NOT NULL,

                payment_method TEXT NOT NULL,

                price INTEGER NOT NULL DEFAULT 0,

                starts_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,

                status TEXT NOT NULL DEFAULT 'active',

                granted_by INTEGER,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- GAME SESSIONS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS game (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                chat_id INTEGER NOT NULL UNIQUE,

                status TEXT NOT NULL DEFAULT 'lobby',

                phase TEXT NOT NULL DEFAULT 'lobby',

                day_number INTEGER NOT NULL DEFAULT 0,

                min_players INTEGER NOT NULL DEFAULT 7,
                max_players INTEGER NOT NULL DEFAULT 35,

                created_by INTEGER NOT NULL,

                started_at TEXT,
                ended_at TEXT,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (created_by)
                    REFERENCES users(id)
                    ON DELETE RESTRICT
            );


            -- ==================================================
            -- GAME PLAYERS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS game_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                game_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,

                role_id TEXT,
                side TEXT,

                alive INTEGER NOT NULL DEFAULT 1,

                joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                eliminated_at TEXT,

                last_word TEXT,

                UNIQUE(game_id, user_id),

                FOREIGN KEY (game_id)
                    REFERENCES game(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- GAME ACTIONS
            -- ==================================================

            CREATE TABLE IF NOT EXISTS game_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                game_id INTEGER NOT NULL,
                actor_id INTEGER NOT NULL,
                target_id INTEGER,

                action_type TEXT NOT NULL,
                phase TEXT NOT NULL,

                result TEXT,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (game_id)
                    REFERENCES game(id)
                    ON DELETE CASCADE
            );


            -- ==================================================
            -- GAME VOTES
            -- ==================================================

            CREATE TABLE IF NOT EXISTS game_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                game_id INTEGER NOT NULL,
                voter_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,

                round_number INTEGER NOT NULL DEFAULT 1,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(
                    game_id,
                    voter_id,
                    round_number
      
