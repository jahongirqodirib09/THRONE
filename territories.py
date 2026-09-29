import random
from database import db, now, ensure_territories, list_territories, get_territory, get_territory_by_name, capture_territory

TERRITORY_TYPES = {
    "village": {"income": 100, "defense": 20},
    "town": {"income": 300, "defense": 60},
    "fortress": {"income": 700, "defense": 150},
    "capital": {"income": 1500, "defense": 300},
}

DEFAULT_MAP = {
    "Shimoliy qishloq": {"type": "village"},
    "Sharqiy qishloq": {"type": "village"},
    "Bozor shahri": {"type": "town"},
    "Chegara qal'asi": {"type": "fortress"},
    "Poytaxt": {"type": "capital"},
}

async def ensure_map():
    defs = {name: {**TERRITORY_TYPES[info["type"]], "type": info["type"]} for name, info in DEFAULT_MAP.items()}
    await ensure_territories(defs)

async def territories():
    await ensure_map()
    return await list_territories()

async def attack(territory_name, clan_id, attack_power):
    territory = await get_territory_by_name(territory_name)
    if not territory:
        return {"ok": False, "error": "not_found"}
    if territory["owner_clan_id"] == clan_id:
        return {"ok": False, "error": "already_owned"}
    chance = attack_power / max(1, attack_power + territory["defense"])
    success = random.random() < chance
    if success:
        await capture_territory(territory["territory_id"], clan_id)
    return {"ok": True, "success": success, "territory": dict(territory)}
