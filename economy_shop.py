# ============================================================
# THRONE — ECONOMY SHOP SYSTEM
# ============================================================

from dataclasses import dataclass
from typing import Optional

from config import CREATOR_ID
from database import (
    get_user,
    get_inventory,
    add_inventory_item,
    spend_balance,
)


# ============================================================
# CURRENCIES
# ============================================================

GOLD = "gold"
COIN = "coin"
DIAMOND = "diamond"


# ============================================================
# ITEM CATEGORIES
# ============================================================

CATEGORY_WEAPON = "weapon"
CATEGORY_ARMOR = "armor"
CATEGORY_CLOTHING = "clothing"
CATEGORY_HORSE = "horse"
CATEGORY_RING = "ring"
CATEGORY_SPECIAL = "special"
CATEGORY_PREMIUM = "premium"


# ============================================================
# RESULT
# ============================================================

@dataclass
class ShopResult:
    success: bool
    message: str
    data: Optional[dict] = None


# ============================================================
# SHOP ITEMS
# ============================================================

SHOP_ITEMS = {

    # --------------------------------------------------------
    # WEAPONS
    # --------------------------------------------------------

    "wooden_sword": {
        "name": "🗡️ Yog‘och qilich",
        "category": CATEGORY_WEAPON,
        "currency": GOLD,
        "price": 500,
        "attack": 5,
        "defense": 0,
        "description": "Boshlang‘ich jang quroli.",
    },

    "iron_sword": {
        "name": "⚔️ Temir qilich",
        "category": CATEGORY_WEAPON,
        "currency": GOLD,
        "price": 2_500,
        "attack": 15,
        "defense": 2,
        "description": "Mustahkam temir qilich.",
    },

    "royal_sword": {
        "name": "👑 Qirollik qilichi",
        "category": CATEGORY_WEAPON,
        "currency": COIN,
        "price": 100,
        "attack": 35,
        "defense": 5,
        "description": "Qirollik jangchilari uchun maxsus qilich.",
    },

    "shadow_blade": {
        "name": "🩸 Shadow Blade",
        "category": CATEGORY_WEAPON,
        "currency": DIAMOND,
        "price": 10,
        "attack": 60,
        "defense": 10,
        "description": "Qora bozorda uchraydigan noyob qurol.",
    },

    # --------------------------------------------------------
    # ARMOR
    # --------------------------------------------------------

    "leather_armor": {
        "name": "🛡️ Charm zirh",
        "category": CATEGORY_ARMOR,
        "currency": GOLD,
        "price": 1_500,
        "attack": 0,
        "defense": 10,
        "description": "Yengil himoya zirhi.",
    },

    "iron_armor": {
        "name": "🛡️ Temir zirh",
        "category": CATEGORY_ARMOR,
        "currency": GOLD,
        "price": 5_000,
        "attack": 2,
        "defense": 30,
        "description": "Og‘ir va mustahkam zirh.",
    },

    "royal_armor": {
        "name": "👑 Qirollik zirhi",
        "category": CATEGORY_ARMOR,
        "currency": COIN,
        "price": 200,
        "attack": 10,
        "defense": 55,
        "description": "Qirollik qo‘riqchilari zirhi.",
    },

    "throne_armor": {
        "name": "⚜️ THRONE zirhi",
        "category": CATEGORY_PREMIUM,
        "currency": DIAMOND,
        "price": 25,
        "attack": 25,
        "defense": 100,
        "description": "Noyob premium zirh.",
    },

    # --------------------------------------------------------
    # CLOTHING
    # --------------------------------------------------------

    "noble_cloak": {
        "name": "🧥 Zodagon plashi",
        "category": CATEGORY_CLOTHING,
        "currency": GOLD,
        "price": 3_000,
        "attack": 0,
        "defense": 5,
        "description": "Zodagonlar kiyadigan qirollik plashi.",
    },

    "royal_cloak": {
        "name": "👑 Qirollik plashi",
        "category": CATEGORY_CLOTHING,
        "currency": COIN,
        "price": 150,
        "attack": 5,
        "defense": 15,
        "description": "Qirollik saroyiga mos plash.",
    },

    "throne_crown": {
        "name": "👑 THRONE toj",
        "category": CATEGORY_PREMIUM,
        "currency": DIAMOND,
        "price": 20,
        "attack": 15,
        "defense": 25,
        "description": "THRONE olamidagi noyob toj.",
    },

    # --------------------------------------------------------
    # HORSES
    # --------------------------------------------------------

    "brown_horse": {
        "name": "🐎 Jigarrang ot",
        "category": CATEGORY_HORSE,
        "currency": GOLD,
        "price": 4_000,
        "attack": 5,
        "defense": 5,
        "speed": 10,
        "description": "Oddiy jangovar ot.",
    },

    "black_horse": {
        "name": "🐎 Qora ot",
        "category": CATEGORY_HORSE,
        "currency": COIN,
        "price": 250,
        "attack": 15,
        "defense": 15,
        "speed": 25,
        "description": "Tez va kuchli ot.",
    },

    "royal_horse": {
        "name": "👑 Qirollik oti",
        "category": CATEGORY_HORSE,
        "currency": DIAMOND,
        "price": 15,
        "attack": 30,
        "defense": 30,
        "speed": 50,
        "description": "Qirollik uchun maxsus ot.",
    },

    # --------------------------------------------------------
    # RINGS
    # --------------------------------------------------------

    "silver_ring": {
        "name": "💍 Kumush uzuk",
        "category": CATEGORY_RING,
        "currency": GOLD,
        "price": 2_000,
        "attack": 0,
        "defense": 10,
        "description": "Oddiy oilaviy aksessuar.",
    },

    "royal_ring": {
        "name": "💍 Qirollik uzugi",
        "category": CATEGORY_RING,
        "currency": COIN,
        "price": 100,
        "attack": 10,
        "defense": 25,
        "description": "Qirollik ramzi.",
    },

    "throne_ring": {
        "name": "💎 THRONE uzugi",
        "category": CATEGORY_PREMIUM,
        "currency": DIAMOND,
        "price": 10,
        "attack": 25,
        "defense": 50,
        "description": "Premium noyob uzuk.",
    },

    # --------------------------------------------------------
    # SPECIAL
    # --------------------------------------------------------

    "royal_banner": {
        "name": "🚩 Qirollik bayrog‘i",
        "category": CATEGORY_SPECIAL,
        "currency": COIN,
        "price": 75,
        "attack": 10,
        "defense": 10,
        "description": "Qirollik profilini bezaydi.",
    },

    "throne_emblem": {
        "name": "⚜️ THRONE emblemasi",
        "category": CATEGORY_PREMIUM,
        "currency": DIAMOND,
        "price": 5,
        "attack": 10,
        "defense": 10,
        "description": "Profil uchun premium emblema.",
    },
}


# ============================================================
# CREATOR
# ============================================================

def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


# ============================================================
# ITEM
# ============================================================

def get_item(
    item_id: str,
) -> Optional[dict]:

    return SHOP_ITEMS.get(
        item_id
    )


def item_exists(
    item_id: str,
) -> bool:

    return item_id in SHOP_ITEMS


# ============================================================
# ITEM NAME
# ============================================================

def item_name(
    item_id: str,
) -> str:

    item = get_item(
        item_id
    )

    if not item:
        return "❔ Noma’lum buyum"

    return item["name"]


# ============================================================
# CATEGORY NAME
# ============================================================

def category_name(
    category: str,
) -> str:

    names = {
        CATEGORY_WEAPON: "⚔️ Qurollar",
        CATEGORY_ARMOR: "🛡️ Zirhlar",
        CATEGORY_CLOTHING: "👕 Kiyimlar",
        CATEGORY_HORSE: "🐎 Otlar",
        CATEGORY_RING: "💍 Uzuklar",
        CATEGORY_SPECIAL: "✨ Maxsus",
        CATEGORY_PREMIUM: "💎 Premium",
    }

    return names.get(
        category,
        "🛒 Boshqa",
    )


# ============================================================
# CURRENCY NAME
# ============================================================

def currency_name(
    currency: str,
) -> str:

    names = {
        GOLD: "🟡 Oltin",
        COIN: "🪙 Coin",
        DIAMOND: "💎 Olmos",
    }

    return names.get(
        currency,
        currency,
    )


# ============================================================
# ITEM STATS
# ============================================================

def item_power(
    item: dict,
) -> int:

    return (
        max(
            0,
            int(item.get("attack", 0)),
        )
        + max(
            0,
            int(item.get("defense", 0)),
        )
        + max(
            0,
            int(item.get("speed", 0)),
        )
    )


# ============================================================
# ITEM TEXT
# ============================================================

def item_text(
    item_id: str,
) -> str:

    item = get_item(
        item_id
    )

    if not item:
        return "❌ Buyum topilmadi."

    lines = [
        item["name"],
        "",
        f"📂 {category_name(item['category'])}",
        f"💰 Narx: {item['price']:,} "
        f"{currency_name(item['currency'])}",
        "",
        f"⚔️ Hujum: +{item.get('attack', 0)}",
        f"🛡️ Himoya: +{item.get('defense', 0)}",
    ]

    if "speed" in item:
        lines.append(
            f"🐎 Tezlik: +{item['speed']}"
        )

    lines.extend(
        [
            "",
            f"✨ Kuch: {item_power(item)}",
            "",
            f"📖 {item['description']}",
        ]
    )

    return "\n".join(
        lines
    )


# ============================================================
# SHOP BY CATEGORY
# ============================================================

def items_by_category(
    category: str,
) -> list:

    result = []

    for item_id, item in SHOP_ITEMS.items():

        if item.get("category") == category:
            result.append(
                {
                    "id": item_id,
                    **item,
                }
            )

    return result


# ============================================================
# SHOP LIST
# ============================================================

def shop_text(
    category: Optional[str] = None,
) -> str:

    if category:

        items = items_by_category(
            category
        )

        title = category_name(
            category
        )

    else:

        items = [
            {
                "id": item_id,
                **item,
            }
            for item_id, item
            in SHOP_ITEMS.items()
        ]

        title = "🛒 THRONE DO‘KONI"

    if not items:
        return (
            f"{title}\n\n"
            "Hozircha bu bo‘limda buyum yo‘q."
        )

    lines = [
        title,
        "",
    ]

    for item in items:

        lines.append(
            f"{item['name']} — "
            f"{item['price']:,} "
            f"{currency_name(item['currency'])}"
        )

    return "\n".join(
        lines
    )


# ============================================================
# PURCHASE VALIDATION
# ============================================================

async def can_purchase(
    user_id: int,
    item_id: str,
) -> ShopResult:

    item = get_item(
        item_id
    )

    if not item:
        return ShopResult(
            False,
            "❌ Buyum topilmadi.",
        )

    user = await get_user(
        user_id
    )

    if not user:
        return ShopResult(
            False,
            "❌ O‘yinchi topilmadi.",
        )

    return ShopResult(
        True,
        "✅ Xarid qilish mumkin.",
        {
            "item": item,
            "user": user,
        },
    )


# ============================================================
# PURCHASE
# ============================================================

async def purchase_item(
    user_id: int,
    item_id: str,
) -> ShopResult:

    validation = await can_purchase(
        user_id,
        item_id,
    )

    if not validation.success:
        return validation

    item = validation.data["item"]

    # Creator uchun do‘kondagi barcha buyumlar bepul.
    if is_creator(user_id):

        inventory_result = await add_inventory_item(
            user_id,
            item_id,
            1,
        )

        return ShopResult(
            True,
            (
                "👑 CREATOR — BUYUM OLINDI\n\n"
                f"{item['name']}\n"
                "💰 Narx: 0\n"
                "♾️ Creator imtiyozi\n\n"
                "🎒 Inventarga qo‘shildi."
            ),
            {
                "item_id": item_id,
                "quantity": 1,
                "free": True,
                "inventory": inventory_result,
            },
        )

    currency = item["currency"]
    price = item["price"]

    try:

        spent = await spend_balance(
            user_id,
            currency,
            price,
        )

    except TypeError:

        return ShopResult(
            False,
            (
                "❌ Valyuta xaridi tizim bilan "
                "moslashtirilmoqda."
            ),
        )

    if not spent:
        return ShopResult(
            False,
            (
                "❌ Mablag‘ yetarli emas.\n\n"
                f"Kerak: {price:,} "
                f"{currency_name(currency)}"
            ),
        )

    try:

        inventory_result = await add_inventory_item(
            user_id,
            item_id,
            1,
        )

    except Exception:

        return ShopResult(
            False,
            (
                "❌ Buyumni inventarga qo‘shishda "
                "xatolik yuz berdi."
            ),
        )

    return ShopResult(
        True,
        (
            "✅ XARID MUVAFFAQIYATLI\n\n"
            f"{item['name']}\n\n"
            f"💰 To‘lov: {price:,} "
            f"{currency_name(currency)}\n"
            "🎒 Inventarga qo‘shildi."
        ),
        {
            "item_id": item_id,
            "quantity": 1,
            "price": price,
            "currency": currency,
            "inventory": inventory_result,
        },
    )


# ============================================================
# MULTIPLE PURCHASE
# ============================================================

async def purchase_multiple(
    user_id: int,
    item_id: str,
    quantity: int,
) -> ShopResult:

    quantity = max(
        1,
        min(
            99,
            int(quantity),
        ),
    )

    item = get_item(
        item_id
    )

    if not item:
        return ShopResult(
            False,
            "❌ Buyum topilmadi.",
        )

    if is_creator(user_id):

        inventory_result = await add_inventory_item(
            user_id,
            item_id,
            quantity,
        )

        return ShopResult(
            True,
            (
                "👑 CREATOR — BUYUMLAR OLINDI\n\n"
                f"{item['name']}\n"
                f"📦 Miqdor: {quantity}\n"
                "♾️ Creator imtiyozi."
            ),
            {
                "quantity": quantity,
                "free": True,
                "inventory": inventory_result,
            },
        )

    total_price = (
        item["price"]
        * quantity
    )

    spent = await spend_balance(
        user_id,
        item["currency"],
        total_price,
    )

    if not spent:
        return ShopResult(
            False,
            (
                "❌ Mablag‘ yetarli emas.\n\n"
                f"📦 Miqdor: {quantity}\n"
                f"💰 Jami: {total_price:,} "
                f"{currency_name(item['currency'])}"
            ),
        )

    inventory_result = await add_inventory_item(
        user_id,
        item_id,
        quantity,
    )

    return ShopResult(
        True,
        (
            "✅ XARID MUVAFFAQIYATLI\n\n"
            f"{item['name']}\n"
            f"📦 Miqdor: {quantity}\n"
            f"💰 Jami: {total_price:,} "
            f"{currency_name(item['currency'])}\n\n"
            "🎒 Inventarga qo‘shildi."
        ),
        {
            "quantity": quantity,
            "total_price": total_price,
            "currency": item["currency"],
            "inventory": inventory_result,
        },
    )


# ============================================================
# INVENTORY CHECK
# ============================================================

async def get_owned_quantity(
    user_id: int,
    item_id: str,
) -> int:

    inventory = await get_inventory(
        user_id
    )

    if not inventory:
        return 0

    if isinstance(
        inventory,
        dict,
    ):

        item = inventory.get(
            item_id
        )

        if isinstance(
            item,
            dict,
        ):
            return int(
                item.get(
                    "quantity",
                    0,
                )
                or 0
            )

        if isinstance(
            item,
            int,
        ):
            return item

    if isinstance(
        inventory,
        list,
    ):

        total = 0

        for row in inventory:

            if not isinstance(
                row,
                dict,
            ):
                continue

            if row.get("item_id") == item_id:
                total += int(
                    row.get(
                        "quantity",
                        0,
                    )
                    or 0
                )

        return total

    return 0


# ============================================================
# EQUIPMENT POWER
# ============================================================

def equipment_power(
    items: list,
) -> dict:

    attack = 0
    defense = 0
    speed = 0

    for item in items:

        if not item:
            continue

        attack += int(
            item.get(
                "attack",
                0,
            )
            or 0
        )

        defense += int(
            item.get(
                "defense",
                0,
            )
            or 0
        )

        speed += int(
            item.get(
                "speed",
                0,
            )
            or 0
        )

    return {
        "attack": attack,
        "defense": defense,
        "speed": speed,
        "total": (
            attack
            + defense
            + speed
        ),
    }


# ============================================================
# ITEM SEARCH
# ============================================================

def search_items(
    query: str,
) -> list:

    query = query.strip().lower()

    if not query:
        return []

    results = []

    for item_id, item in SHOP_ITEMS.items():

        searchable = (
            item_id.lower()
            + " "
            + item["name"].lower()
            + " "
            + item["description"].lower()
        )

        if query in searchable:

            results.append(
                {
                    "id": item_id,
                    **item,
                }
            )

    return results


# ============================================================
# SHOP SUMMARY
# ============================================================

def shop_summary() -> dict:

    categories = {}

    for item in SHOP_ITEMS.values():

        category = item.get(
            "category",
            "other",
        )

        categories[category] = (
            categories.get(
                category,
                0,
            )
            + 1
        )

    return {
        "total_items": len(
         
