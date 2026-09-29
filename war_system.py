import random
from database import get_user_clan, get_clan, get_active_war, create_war, add_war_score, finish_war, db

async def declare_war(attacker_id, defender_clan_name):
    from database import get_clan_by_name
    attacker_clan = await get_user_clan(attacker_id)
    if not attacker_clan:
        return {"ok": False, "error": "no_clan"}
    if attacker_clan.get("position") != "leader":
        return {"ok": False, "error": "not_leader"}
    defender = await get_clan_by_name(defender_clan_name)
    if not defender:
        return {"ok": False, "error": "target_not_found"}
    if defender["clan_id"] == attacker_clan["clan_id"]:
        return {"ok": False, "error": "self_war"}
    if await get_active_war(attacker_clan["clan_id"]):
        return {"ok": False, "error": "already_at_war"}
    war_id = await create_war(attacker_clan["clan_id"], defender["clan_id"])
    return {"ok": True, "war_id": war_id, "attacker": attacker_clan["name"], "defender": defender["name"]}

async def attack_round(war_id, attacker_power, defender_power):
    chance = attacker_power / max(1, attacker_power + defender_power)
    won = random.random() < chance
    await add_war_score(war_id, "attacker" if won else "defender", 1)
    return won

async def try_finish_war(war_id, score_to_win=3):
    from database import get_war
    war = await get_war(war_id)
    if not war or war["status"] != "ACTIVE":
        return None
    if war["attacker_score"] >= score_to_win:
        await finish_war(war_id, war["attacker_clan_id"])
        return war["attacker_clan_id"]
    if war["defender_score"] >= score_to_win:
        await finish_war(war_id, war["defender_clan_id"])
        return war["defender_clan_id"]
    return None
