from database import inventory_add
from economy import spend

ITEMS = {
    "shadow_blade": ("🗡️ Shadow Blade", 2500, "gold"),
    "dark_crown": ("👑 Dark Crown", 150, "diamond"),
    "black_cloak": ("🖤 Black Cloak", 1000, "gold"),
    "ancient_weapon": ("⚔️ Ancient Weapon", 250, "diamond"),
}

async def buy(user_id, item_key):
    item = ITEMS.get(item_key)
    if not item:
        return {"ok": False, "error": "not_found"}
    name, price, currency = item
    if not await spend(user_id, currency, price):
        return {"ok": False, "error": "not_enough_funds"}
    await inventory_add(user_id, item_key)
    return {"ok": True, "name": name, "price": price, "currency": currency}

def list_text():
    lines = [f"• {key}: {name} — {price} {currency}" for key, (name, price, currency) in ITEMS.items()]
    return "🕶️ QORA BOZOR\n\n" + "\n".join(lines)
