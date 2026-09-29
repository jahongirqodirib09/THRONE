from __future__ import annotations
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import aiosqlite
from config import DATABASE_PATH, CREATOR_ID

def now():
    return datetime.now(timezone.utc).isoformat()

@asynccontextmanager
async def db():
    conn = await aiosqlite.connect(DATABASE_PATH)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA foreign_keys=ON")
    await conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        await conn.commit()
    except:
        await conn.rollback()
        raise
    finally:
        await conn.close()

async def init_db():
    async with db() as c:
        await c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT NOT NULL,
            gold INTEGER NOT NULL DEFAULT 1000, coin INTEGER NOT NULL DEFAULT 100,
            diamond INTEGER NOT NULL DEFAULT 0, xp INTEGER NOT NULL DEFAULT 0,
            level INTEGER NOT NULL DEFAULT 1, elite_until TEXT, elite_permanent INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL, last_active TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS chats(chat_id INTEGER PRIMARY KEY, title TEXT, type TEXT, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS games(
            game_id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER NOT NULL,
            status TEXT NOT NULL, phase TEXT NOT NULL, day INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL, started_at TEXT, ended_at TEXT
        );
        CREATE UNIQUE INDEX IF NOT EXISTS one_active_game ON games(chat_id) WHERE status IN ('LOBBY','RUNNING');
        CREATE TABLE IF NOT EXISTS game_players(
            game_id INTEGER NOT NULL, user_id INTEGER NOT NULL, role_id TEXT,
            alive INTEGER NOT NULL DEFAULT 1, joined_at TEXT NOT NULL,
            PRIMARY KEY(game_id,user_id)
        );
        CREATE TABLE IF NOT EXISTS game_actions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, game_id INTEGER NOT NULL, day INTEGER NOT NULL,
            actor_id INTEGER NOT NULL, action TEXT NOT NULL, target_id INTEGER,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS game_votes(
            id INTEGER PRIMARY KEY AUTOINCREMENT, game_id INTEGER NOT NULL, day INTEGER NOT NULL,
            voter_id INTEGER NOT NULL, target_id INTEGER NOT NULL,
            UNIQUE(game_id,day,voter_id)
        );
        CREATE TABLE IF NOT EXISTS inventory(
            user_id INTEGER NOT NULL, item_id TEXT NOT NULL, quantity INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY(user_id,item_id)
        );
        CREATE TABLE IF NOT EXISTS clans(
            clan_id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER NOT NULL,
            name TEXT UNIQUE NOT NULL, description TEXT DEFAULT '', level INTEGER DEFAULT 1,
            power INTEGER DEFAULT 0, treasury INTEGER DEFAULT 0, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS clan_members(
            clan_id INTEGER NOT NULL, user_id INTEGER NOT NULL, position TEXT DEFAULT 'member',
            PRIMARY KEY(clan_id,user_id)
        );
        CREATE TABLE IF NOT EXISTS couples(
            user1_id INTEGER NOT NULL, user2_id INTEGER NOT NULL, status TEXT NOT NULL,
            created_at TEXT NOT NULL, PRIMARY KEY(user1_id,user2_id)
        );
        CREATE TABLE IF NOT EXISTS couple_proposals(
            id INTEGER PRIMARY KEY AUTOINCREMENT, from_id INTEGER NOT NULL, to_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending', created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS duels(
            duel_id INTEGER PRIMARY KEY AUTOINCREMENT, challenger INTEGER NOT NULL,
            opponent INTEGER NOT NULL, status TEXT NOT NULL, winner INTEGER, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS elite_grants(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            days INTEGER, permanent INTEGER DEFAULT 0, granted_by INTEGER NOT NULL,
            created_at TEXT NOT NULL, expires_at TEXT
        );
        CREATE TABLE IF NOT EXISTS security_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, event TEXT, details TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS missions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, title TEXT, reward_gold INTEGER DEFAULT 0,
            reward_coin INTEGER DEFAULT 0, reward_diamond INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS player_missions(
            user_id INTEGER, mission_id INTEGER, progress INTEGER DEFAULT 0, claimed INTEGER DEFAULT 0,
            PRIMARY KEY(user_id,mission_id)
        );
        CREATE TABLE IF NOT EXISTS scheduled_jobs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, job_type TEXT, payload TEXT, run_at TEXT, done INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS territories(
            territory_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL DEFAULT 'village', owner_clan_id INTEGER, income INTEGER DEFAULT 100,
            defense INTEGER DEFAULT 20, captured_at TEXT
        );
        CREATE TABLE IF NOT EXISTS clan_wars(
            war_id INTEGER PRIMARY KEY AUTOINCREMENT, attacker_clan_id INTEGER NOT NULL,
            defender_clan_id INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'ACTIVE',
            attacker_score INTEGER DEFAULT 0, defender_score INTEGER DEFAULT 0,
            winner_clan_id INTEGER, created_at TEXT NOT NULL, ended_at TEXT
        );
        CREATE TABLE IF NOT EXISTS royal_court(
            position TEXT PRIMARY KEY, user_id INTEGER, granted_at TEXT
        );
        CREATE TABLE IF NOT EXISTS channels(
            channel_id INTEGER PRIMARY KEY, title TEXT DEFAULT '', username TEXT DEFAULT '',
            reward_gold INTEGER DEFAULT 0, required INTEGER DEFAULT 0, active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS channel_claims(
            user_id INTEGER NOT NULL, channel_id INTEGER NOT NULL, claimed_at TEXT NOT NULL,
            PRIMARY KEY(user_id, channel_id)
        );
        CREATE TABLE IF NOT EXISTS payments(
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            payload TEXT UNIQUE NOT NULL, plan TEXT NOT NULL, amount INTEGER NOT NULL,
            currency TEXT DEFAULT 'XTR', status TEXT DEFAULT 'pending',
            charge_id TEXT, created_at TEXT NOT NULL, completed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS tournament_players(
            tournament_id INTEGER NOT NULL, user_id INTEGER NOT NULL, score INTEGER DEFAULT 0,
            joined_at TEXT NOT NULL, PRIMARY KEY(tournament_id, user_id)
        );
        """)


async def ensure_user(user_id, username="", full_name="Player"):
    async with db() as c:
        await c.execute("""INSERT INTO users(user_id,username,full_name,created_at,last_active)
        VALUES(?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,
        full_name=excluded.full_name,last_active=excluded.last_active""",
        (user_id, username or "", full_name or "Player", now()))

async def get_user(user_id):
    async with db() as c:
        cur = await c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return await cur.fetchone()

async def change_balance(user_id, currency, amount):
    if currency not in {"gold","coin","diamond"}: return False
    if user_id == CREATOR_ID: return True
    async with db() as c:
        row = await c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = await row.fetchone()
        if not user or user[currency] + amount < 0: return False
        await c.execute(f"UPDATE users SET {currency}={currency}+? WHERE user_id=?", (amount,user_id))
        return True

async def inventory_add(user_id,item_id,qty=1):
    async with db() as c:
        await c.execute("""INSERT INTO inventory VALUES(?,?,?)
        ON CONFLICT(user_id,item_id) DO UPDATE SET quantity=quantity+excluded.quantity""",
        (user_id,item_id,qty))

async def get_inventory(user_id):
    async with db() as c:
        cur=await c.execute("SELECT item_id,quantity FROM inventory WHERE user_id=?", (user_id,))
        return [dict(x) for x in await cur.fetchall()]

async def active_game(chat_id):
    async with db() as c:
        cur=await c.execute("SELECT * FROM games WHERE chat_id=? AND status IN ('LOBBY','RUNNING')", (chat_id,))
        return await cur.fetchone()

async def game_players(game_id):
    async with db() as c:
        cur=await c.execute("""SELECT gp.*,u.full_name,u.username FROM game_players gp
        JOIN users u ON u.user_id=gp.user_id WHERE game_id=? ORDER BY joined_at""",(game_id,))
        return [dict(x) for x in await cur.fetchall()]


# ============================================================
# CLANS (extra helpers)
# ============================================================

async def get_clan(clan_id):
    async with db() as c:
        cur = await c.execute("SELECT * FROM clans WHERE clan_id=?", (clan_id,))
        return await cur.fetchone()

async def get_clan_by_name(name):
    async with db() as c:
        cur = await c.execute("SELECT * FROM clans WHERE name=? COLLATE NOCASE", (name,))
        return await cur.fetchone()

async def get_user_clan(user_id):
    async with db() as c:
        cur = await c.execute(
            "SELECT cl.*, cm.position FROM clans cl JOIN clan_members cm ON cm.clan_id=cl.clan_id "
            "WHERE cm.user_id=?", (user_id,))
        return await cur.fetchone()

async def clan_members(clan_id):
    async with db() as c:
        cur = await c.execute(
            "SELECT cm.*, u.full_name, u.username FROM clan_members cm "
            "JOIN users u ON u.user_id=cm.user_id WHERE cm.clan_id=?", (clan_id,))
        return [dict(x) for x in await cur.fetchall()]

async def list_clans(limit=10):
    async with db() as c:
        cur = await c.execute("SELECT * FROM clans ORDER BY power DESC, level DESC LIMIT ?", (limit,))
        return [dict(x) for x in await cur.fetchall()]

async def leave_clan_db(user_id):
    async with db() as c:
        await c.execute("DELETE FROM clan_members WHERE user_id=?", (user_id,))


# ============================================================
# ROYAL COURT
# ============================================================

async def get_king():
    async with db() as c:
        cur = await c.execute("SELECT * FROM royal_court WHERE position='Shoh'")
        return await cur.fetchone()

async def get_position_holder(position):
    async with db() as c:
        cur = await c.execute("SELECT * FROM royal_court WHERE position=?", (position,))
        return await cur.fetchone()

async def set_position(position, user_id):
    async with db() as c:
        await c.execute(
            "INSERT INTO royal_court(position,user_id,granted_at) VALUES(?,?,?) "
            "ON CONFLICT(position) DO UPDATE SET user_id=excluded.user_id, granted_at=excluded.granted_at",
            (position, user_id, now()))

async def clear_position(position):
    async with db() as c:
        await c.execute("DELETE FROM royal_court WHERE position=?", (position,))

async def list_court():
    async with db() as c:
        cur = await c.execute(
            "SELECT rc.position, rc.user_id, u.full_name FROM royal_court rc "
            "JOIN users u ON u.user_id=rc.user_id")
        return [dict(x) for x in await cur.fetchall()]


# ============================================================
# TERRITORIES
# ============================================================

async def list_territories():
    async with db() as c:
        cur = await c.execute(
            "SELECT t.*, cl.name AS clan_name FROM territories t "
            "LEFT JOIN clans cl ON cl.clan_id=t.owner_clan_id ORDER BY t.territory_id")
        return [dict(x) for x in await cur.fetchall()]

async def get_territory(territory_id):
    async with db() as c:
        cur = await c.execute("SELECT * FROM territories WHERE territory_id=?", (territory_id,))
        return await cur.fetchone()

async def get_territory_by_name(name):
    async with db() as c:
        cur = await c.execute("SELECT * FROM territories WHERE name=?", (name,))
        return await cur.fetchone()

async def ensure_territories(defs):
    async with db() as c:
        for name, info in defs.items():
            await c.execute(
                "INSERT OR IGNORE INTO territories(name,type,income,defense) VALUES(?,?,?,?)",
                (name, info.get("type", "village"), info.get("income", 100), info.get("defense", 20)))

async def capture_territory(territory_id, clan_id):
    async with db() as c:
        await c.execute(
            "UPDATE territories SET owner_clan_id=?, captured_at=? WHERE territory_id=?",
            (clan_id, now(), territory_id))


# ============================================================
# CLAN WARS
# ============================================================

async def create_war(attacker_clan_id, defender_clan_id):
    async with db() as c:
        cur = await c.execute(
            "INSERT INTO clan_wars(attacker_clan_id,defender_clan_id,status,created_at) VALUES(?,?,?,?)",
            (attacker_clan_id, defender_clan_id, "ACTIVE", now()))
        return cur.lastrowid

async def get_active_war(clan_id):
    async with db() as c:
        cur = await c.execute(
            "SELECT * FROM clan_wars WHERE status='ACTIVE' AND (attacker_clan_id=? OR defender_clan_id=?) "
            "ORDER BY war_id DESC LIMIT 1", (clan_id, clan_id))
        return await cur.fetchone()

async def get_war(war_id):
    async with db() as c:
        cur = await c.execute("SELECT * FROM clan_wars WHERE war_id=?", (war_id,))
        return await cur.fetchone()

async def add_war_score(war_id, side, points):
    col = "attacker_score" if side == "attacker" else "defender_score"
    async with db() as c:
        await c.execute(f"UPDATE clan_wars SET {col}={col}+? WHERE war_id=?", (points, war_id))

async def finish_war(war_id, winner_clan_id):
    async with db() as c:
        await c.execute(
            "UPDATE clan_wars SET status='FINISHED', winner_clan_id=?, ended_at=? WHERE war_id=?",
            (winner_clan_id, now(), war_id))


# ============================================================
# CHANNELS
# ============================================================

async def list_channels(required_only=False):
    q = "SELECT * FROM channels WHERE active=1"
    if required_only:
        q += " AND required=1"
    async with db() as c:
        cur = await c.execute(q)
        return [dict(x) for x in await cur.fetchall()]

async def add_channel(channel_id, title="", username="", reward_gold=0, required=False):
    async with db() as c:
        await c.execute(
            "INSERT INTO channels(channel_id,title,username,reward_gold,required) VALUES(?,?,?,?,?) "
            "ON CONFLICT(channel_id) DO UPDATE SET title=excluded.title, username=excluded.username, "
            "reward_gold=excluded.reward_gold, required=excluded.required, active=1",
            (channel_id, title, username, reward_gold, int(required)))

async def claim_channel(user_id, channel_id):
    async with db() as c:
        cur = await c.execute("SELECT reward_gold FROM channels WHERE channel_id=? AND active=1", (channel_id,))
        ch = await cur.fetchone()
        if not ch or not ch["reward_gold"]:
            return 0
        cur = await c.execute(
            "INSERT OR IGNORE INTO channel_claims(user_id,channel_id,claimed_at) VALUES(?,?,?)",
            (user_id, channel_id, now()))
        if cur.rowcount == 0:
            return 0
        await c.execute("UPDATE users SET gold=gold+? WHERE user_id=?", (ch["reward_gold"], user_id))
        return ch["reward_gold"]


# ============================================================
# PAYMENTS
# ============================================================

async def create_payment(user_id, payload, plan, amount, currency="XTR"):
    async with db() as c:
        await c.execute(
            "INSERT INTO payments(user_id,payload,plan,amount,currency,status,created_at) "
            "VALUES(?,?,?,?,?,?,?)", (user_id, payload, plan, amount, currency, "pending", now()))

async def get_payment(payload):
    async with db() as c:
        cur = await c.execute("SELECT * FROM payments WHERE payload=?", (payload,))
        return await cur.fetchone()

async def complete_payment(payload, charge_id):
    async with db() as c:
        cur = await c.execute(
            "UPDATE payments SET status='completed', charge_id=?, completed_at=? "
            "WHERE payload=? AND status!='completed'", (charge_id, now(), payload))
        return cur.rowcount > 0


# ============================================================
# TOURNAMENTS (extra helpers)
# ============================================================

async def get_tournament(tid):
    async with db() as c:
        cur = await c.execute("SELECT * FROM tournaments WHERE id=?", (tid,))
        return await cur.fetchone()

async def open_tournaments():
    async with db() as c:
        cur = await c.execute("SELECT * FROM tournaments WHERE status='OPEN' ORDER BY id DESC")
        return [dict(x) for x in await cur.fetchall()]

async def join_tournament(tid, user_id):
    async with db() as c:
        await c.execute(
            "INSERT OR IGNORE INTO tournament_players(tournament_id,user_id,joined_at) VALUES(?,?,?)",
            (tid, user_id, now()))

async def tournament_players_list(tid):
    async with db() as c:
        cur = await c.execute(
            "SELECT tp.*, u.full_name FROM tournament_players tp JOIN users u ON u.user_id=tp.user_id "
            "WHERE tp.tournament_id=? ORDER BY tp.score DESC", (tid,))
        return [dict(x) for x in await cur.fetchall()]

async def close_tournament(tid, winner_id=None):
    async with db() as c:
        await c.execute("UPDATE tournaments SET status='CLOSED' WHERE id=?", (tid,))
