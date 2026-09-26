from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timezone

from database import get_user, spend_balance, add_inventory_item


CURRENCY_GOLD = "gold"
CURRENCY_COIN = "coin"
CURRENCY_DIAMOND = "diamond"

MARKET_OPEN = "open"
MARKET_CLOSED = "closed"

CREATOR_MARKET_ACCESS = True


BLACK_MARKET_ITEMS: Dict[str, dict] = {
    "shadow_blade": {
        "name": "🗡️ Soya Tig‘i",
        "category": "weapon",
        "currency": CURRENCY_DIAMOND,
        "price": 35,
        "power": 18,
        "stock": 3,
        "description": "Yashirin janglar uchun noyob qilich.",
    },
    "royal_armor": {
        "name": "🛡️ Qora Qirol Zirhi",
        "category": "armor",
        "currency": CURRENCY_DIAMOND,
        "price": 50,
        "power": 25,
        "stock": 2,
        "description": "Qirollik jangchilari uchun noyob zirh.",
    },
    "night_horse": {
        "name": "🐎 Tungi Tulpor",
        "category": "horse",
        "currency": CURRENCY_COIN,
        "price": 900,
        "power": 14,
        "stock": 5,
        "description": "Tezkor va noyob ot.",
    },
    "dark_crown": {
        "name": "👑 Qora Toj",
        "category": "special",
        "currency": CURRENCY_DIAMOND,
        "price": 100,
        "power": 40,
        "stock": 1,
        "description": "Juda kam uchraydigan qirollik artefakti.",
    },
    "shadow_ring": {
        "name": "💍 Soya Uzugi",
        "category": "ring",
        "currency": CURRENCY_COIN,
        "price": 1200,
        "power": 10,
        "stock": 4,
        "description": "Maxsus himoya bonusini beruvchi uzuk.",
    },
    "black_cloak": {
        "name": "🧥 Qora Qirol Yopinchiği",
        "category": "clothing",
        "currency": CURRENCY_COIN,
        "price": 750,
        "power": 8,
        "stock": 6,
        "description": "Qirollik saroyidagi noyob kiyim.",
    },
    "royal_horse": {
        "name": "🐎 Qirollik Tulpori",
        "category": "horse",
        "currency": CURRENCY_DIAMOND,
        "price": 30,
        "power": 20,
        "stock": 3,
        "description": "Qirollik uchun maxsus tayyorlangan tulpor.",
    },
    "ancient_weapon": {
        "name": "⚔️ Qadimiy Qilich",
        "category": "weapon",
        "currency": CURRENCY_COIN,
        "price": 1500,
        "power": 30,
        "stock": 2,
        "description": "Qadimiy jangchilardan qolgan qurol.",
    },
    "diamond_chest": {
        "name": "💎 Sirli Sandıq",
        "category": "special",
        "currency": CURRENCY_DIAMOND,
        "price": 15,
        "power": 0,
        "stock": 10,
        "description": "Tasodifiy noyob mukofot olish imkonini beradi.",
    },
    "war_banner": {
        "name": "🏴 Qora Urush Bayrog‘i",
        "category": "special",
        "currency": CURRENCY_COIN,
        "price": 2000,
        "power": 35,
        "stock": 2,
        "description": "Klan va qirollik urushlari uchun maxsus bayroq.",
    },
}


@dataclass
class BlackMarketResult:
    success: bool
    message: str = ""
    item_id: Optional[str] = None
    data: Optional[dict] = None


def get_item(item_id: str) -> Optional[dict]:
    return BLACK_MARKET_ITEMS.get(item_id)


def get_all_items() -> Dict[str, dict]:
    return BLACK_MARKET_ITEMS.copy()


def get_market_categories() -> List[str]:
    categories = set()

    for item in BLACK_MARKET_ITEMS.values():
        categories.add(item["category"])

    return sorted(categories)


def get_currency_name(currency: str) -> str:
    names = {
        CURRENCY_GOLD: "🟡 Oltin",
        CURRENCY_COIN: "🪙 Coin",
        CURRENCY_DIAMOND: "💎 Olmos",
    }

    return names.get(currency, currency)


def get_market_status() -> str:
    return MARKET_OPEN


def is_market_open() -> bool:
    return get_market_status() == MARKET_OPEN


def get_stock(item_id: str) -> int:
    item = get_item(item_id)

    if not item:
        return 0

    return max(0, int(item.get("stock", 0)))


def has_stock(item_id: str, quantity: int = 1) -> bool:
    if quantity <= 0:
        return False

    return get_stock(item_id) >= quantity


def calculate_price(item_id: str, quantity: int = 1) -> int:
    item = get_item(item_id)

    if not item or quantity <= 0:
        return 0

    return int(item["price"]) * quantity


def get_item_power(item_id: str) -> int:
    item = get_item(item_id)

    if not item:
        return 0

    return int(item.get("power", 0))


def get_item_text(item_id: str) -> str:
    item = get_item(item_id)

    if not item:
        return "❌ Mahsulot topilmadi."

    currency = get_currency_name(item["currency"])

    stock = get_stock(item_id)

    return (
        f"{item['name']}\n\n"
        f"📦 Kategoriya: {item['category']}\n"
        f"💰 Narx: {item['price']} {currency}\n"
        f"⚔️ Kuch: +{item['power']}\n"
        f"📦 Qoldiq: {stock} dona\n\n"
        f"📖 {item['description']}"
    )


def get_market_list(
    category: Optional[str] = None,
) -> List[dict]:

    result = []

    for item_id, item in BLACK_MARKET_ITEMS.items():

        if category and item["category"] != category:
            continue

        result.append(
            {
                "id": item_id,
                **item,
                "stock": get_stock(item_id),
                "currency_name": get_currency_name(
                    item["currency"]
                ),
            }
        )

    return result


def get_market_text(
    category: Optional[str] = None,
) -> str:

    items = get_market_list(category)

    lines = [
        "🕶️ QORA BOZOR",
        "",
        "⚠️ Bu yerda oddiy do‘konlarda uchramaydigan",
        "noyob va cheklangan mahsulotlar sotiladi.",
        "",
    ]

    if not items:
        lines.append("❌ Hozircha mahsulot mavjud emas.")
        return "\n".join(lines)

    for item in items:
        lines.extend(
            [
                f"{item['name']}",
                f"💰 {item['price']} {item['currency_name']}",
                f"⚔️ Kuch: +{item['power']}",
                f"📦 Qoldiq: {item['stock']}",
                "",
            ]
        )

    return "\n".join(lines)


def validate_purchase(
    user_id: int,
    item_id: str,
    quantity: int = 1,
) -> BlackMarketResult:

    if not is_market_open():
        return BlackMarketResult(
            success=False,
            message="🕶️ Qora bozor hozir yopiq.",
        )

    if quantity <= 0:
        return BlackMarketResult(
            success=False,
            message="❌ Miqdor noto‘g‘ri.",
        )

    item = get_item(item_id)

    if not item:
        return BlackMarketResult(
            success=False,
            message="❌ Mahsulot topilmadi.",
        )

    if not has_stock(item_id, quantity):
        return BlackMarketResult(
            success=False,
            message="❌ Mahsulotning yetarli qoldig‘i yo‘q.",
        )

    total_price = calculate_price(
        item_id,
        quantity,
    )

    return BlackMarketResult(
        success=True,
        message="✅ Xarid qilish mumkin.",
        item_id=item_id,
        data={
            "item": item,
            "quantity": quantity,
            "total_price": total_price,
            "currency": item["currency"],
        },
    )


async def is_creator(user_id: int) -> bool:
    try:
        from config import CREATOR_ID

        return user_id == CREATOR_ID
    except Exception:
        return False


async def purchase_item(
    user_id: int,
    item_id: str,
    quantity: int = 1,
) -> BlackMarketResult:

    validation = validate_purchase(
        user_id,
        item_id,
        quantity,
    )

    if not validation.success:
        return validation

    item = get_item(item_id)

    if not item:
        return BlackMarketResult(
            success=False,
            message="❌ Mahsulot topilmadi.",
        )

    creator = await is_creator(user_id)

    total_price = calculate_price(
        item_id,
        quantity,
    )

    currency = item["currency"]

    if not creator:
        try:
            paid = await spend_balance(
                user_id,
                currency,
                total_price,
            )
        except Exception as exc:
            return BlackMarketResult(
                success=False,
                message=f"❌ To‘lovni amalga oshirib bo‘lmadi: {exc}",
            )

        if not paid:
            return BlackMarketResult(
                success=False,
                message=(
                    f"❌ Mablag‘ yetarli emas.\n"
                    f"Kerak: {total_price} "
                    f"{get_currency_name(currency)}"
                ),
            )

    try:
        await add_inventory_item(
            user_id,
            item_id,
            quantity,
        )
    except Exception as exc:
        return BlackMarketResult(
            success=False,
            message=f"❌ Mahsulot inventarga qo‘shilmadi: {exc}",
        )

    return BlackMarketResult(
        success=True,
        item_id=item_id,
        message=(
            "🕶️ QORA BOZOR\n\n"
            f"✅ {item['name']} xarid qilindi.\n"
            f"📦 Miqdor: {quantity}\n"
            f"⚔️ Kuch: +{item['power'] * quantity}\n"
            + (
                "\n𓆩 ELITE YARATUVCHI 𓆪\n"
                "💎 Xarid narxi: 0"
                if creator
                else ""
            )
        ),
        data={
            "item_id": item_id,
            "quantity": quantity,
            "price": total_price,
            "currency": currency,
            "creator": creator,
        },
    )


def purchase_preview(
    item_id: str,
    quantity: int = 1,
) -> str:

    validation = validate_purchase(
        0,
        item_id,
        quantity,
    )

    if not validation.success:
        return validation.message

    item = get_item(item_id)

    if not item:
        return "❌ Mahsulot topilmadi."

    total = calculate_price(
        item_id,
        quantity,
    )

    return (
        "🕶️ QORA BOZOR — XARID\n\n"
        f"{item['name']}\n\n"
        f"📦 Miqdor: {quantity}\n"
        f"💰 Jami: {total} "
        f"{get_currency_name(item['currency'])}\n"
        f"⚔️ Umumiy kuch: +{item['power'] * quantity}\n\n"
        "Tasdiqlashdan oldin ma'lumotlarni tekshiring."
    )


def get_rare_items() -> List[dict]:
    return [
        {
            "id": item_id,
            **item,
        }
        for item_id, item in BLACK_MARKET_ITEMS.items()
        if item.get("power", 0) >= 20
    ]


def get_limited_items() -> List[dict]:
    return [
        {
            "id": item_id,
            **item,
        }
        for item_id, item in BLACK_MARKET_ITEMS.items()
        if item.get("stock", 0) <= 3
    ]


def get_items_by_currency(currency: str) -> List[dict]:
    return [
        {
            "id": item_id,
            **item,
        }
        for item_id, item in BLACK_MARKET_ITEMS.items()
        if item.get("currency") == currency
    ]


def get_items_by_category(category: str) -> List[dict]:
    return [
        {
            "id": item_id,
            **item,
        }
        for item_id, item in BLACK_MARKET_ITEMS.items()
        if item.get("category") == category
    ]


def market_statistics() -> dict:
    items = list(BLACK_MARKET_ITEMS.values())

    total_stock = sum(
        int(item.get("stock", 0))
        for item in items
    )

    total_power = sum(
        int(item.get("power", 0))
        for item in items
    )

    return {
        "status": get_market_status(),
        "items": len(items),
        "categories": len(get_market_categories()),
        "total_stock": total_stock,
        "total_power": total_power,
        "rare_items": len(get_rare_items()),
        "limited_items": len(get_limited_items()),
    }


def market_dashboard() -> str:
    stats = market_statistics()

    status = (
        "🟢 OCHIQ"
        if stats["status"] == MARKET_OPEN
        else "🔴 YOPIQ"
    )

    return (
        "🕶️ THRONE QORA BOZORI\n\n"
        f"Holat: {status}\n"
        f"📦 Mahsulotlar: {stats['items']}\n"
        f"🗂️ Kategoriyalar: {stats['categories']}\n"
        f"📦 Umumiy qoldiq: {stats['total_stock']}\n"
        f"⚔️ Umumiy kuch: {stats['total_power']}\n"
        f"💎 Noyob mahsulotlar: {stats['rare_items']}\n"
        f"🔥 Cheklangan mahsulotlar: {stats['limited_items']}"
    )


def get_special_offer_items() -> List[dict]:
    return [
        {
            "id": item_id,
            **item,
            "offer": True,
        }
        for item_id, item in BLACK_MARKET_ITEMS.items()
        if item.get("stock", 0) <= 2
    ]


def get_special_offer_text() -> str:
    items = get_special_offer_items()

    if not items:
        return "🕶️ Hozircha maxsus taklif yo‘q."

    lines = [
        "🔥 QORA BOZOR — MAXSUS TAKLIFLAR",
        "",
    ]

    for item in items:
        lines.append(
            f"{item['name']} — "
            f"{item['price']} "
            f"{get_currency_name(item['currency'])}"
        )

    return "\n".join(lines)


def market_reset_info() -> dict:
    return {
        "reset_required": False,
        "last_update": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def serialize_market() -> dict:
    return {
        "status": get_market_status(),
        "items": {
            item_id: dict(item)
            for item_id, item in BLACK_MARKET_ITEMS.items()
        },
        "statistics": market_statistics(),
    }
