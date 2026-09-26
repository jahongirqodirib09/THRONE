from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from database import get_user, execute


ELITE_FREE = "free"
ELITE_ACTIVE = "active"
ELITE_EXPIRED = "expired"

PLAN_7D = "7d"
PLAN_30D = "30d"
PLAN_90D = "90d"
PLAN_180D = "180d"
PLAN_365D = "365d"


ELITE_PLANS: Dict[str, dict] = {
    PLAN_7D: {
        "name": "7 kunlik Elite",
        "days": 7,
        "price": 1.0,
        "currency": "USD",
    },
    PLAN_30D: {
        "name": "30 kunlik Elite",
        "days": 30,
        "price": 3.0,
        "currency": "USD",
    },
    PLAN_90D: {
        "name": "90 kunlik Elite",
        "days": 90,
        "price": 7.0,
        "currency": "USD",
    },
    PLAN_180D: {
        "name": "180 kunlik Elite",
        "days": 180,
        "price": 12.0,
        "currency": "USD",
    },
    PLAN_365D: {
        "name": "365 kunlik Elite",
        "days": 365,
        "price": 20.0,
        "currency": "USD",
    },
}


ELITE_FEATURES = [
    "⚜️ Maxsus Elite belgisi",
    "💎 Premium profil bezaklari",
    "👑 Maxsus THRONE avatar imkoniyatlari",
    "🎁 Qo‘shimcha bonuslar",
    "🏆 Maxsus Elite mukofotlari",
    "🕶️ Qora Bozordagi maxsus imkoniyatlar",
    "🎨 Premium Mini App ko‘rinishlari",
]


@dataclass
class EliteResult:
    success: bool
    message: str = ""
    plan_id: Optional[str] = None
    expires_at: Optional[str] = None
    data: Optional[dict] = None


def get_plan(plan_id: str) -> Optional[dict]:
    return ELITE_PLANS.get(plan_id)


def get_all_plans() -> Dict[str, dict]:
    return {
        plan_id: dict(plan)
        for plan_id, plan in ELITE_PLANS.items()
    }


def get_plan_list() -> List[dict]:
    return [
        {
            "id": plan_id,
            **plan,
        }
        for plan_id, plan in ELITE_PLANS.items()
    ]


def is_valid_plan(plan_id: str) -> bool:
    return plan_id in ELITE_PLANS


async def is_creator(user_id: int) -> bool:
    try:
        from config import CREATOR_ID

        return int(user_id) == int(CREATOR_ID)

    except Exception:
        return False


async def get_elite_record(user_id: int) -> Optional[dict]:
    try:
        row = await execute(
            """
            SELECT *
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
            fetch=True,
        )

        return row

    except Exception:
        return None


async def get_elite_status(user_id: int) -> str:
    if await is_creator(user_id):
        return ELITE_ACTIVE

    try:
        user = await get_user(user_id)

        if not user:
            return ELITE_FREE

        elite_active = user.get("elite_active", 0)
        elite_expires_at = user.get("elite_expires_at")

        if not elite_active:
            return ELITE_FREE

        if not elite_expires_at:
            return ELITE_FREE

        expires = datetime.fromisoformat(
            str(elite_expires_at)
        )

        if expires.tzinfo is None:
            expires = expires.replace(
                tzinfo=timezone.utc
            )

        if expires <= datetime.now(timezone.utc):
            return ELITE_EXPIRED

        return ELITE_ACTIVE

    except Exception:
        return ELITE_FREE


async def has_elite(user_id: int) -> bool:
    return (
        await get_elite_status(user_id)
        == ELITE_ACTIVE
        or await is_creator(user_id)
    )


def calculate_expiry(
    days: int,
    current_expiry: Optional[str] = None,
) -> datetime:

    now = datetime.now(timezone.utc)

    if current_expiry:
        try:
            existing = datetime.fromisoformat(
                str(current_expiry)
            )

            if existing.tzinfo is None:
                existing = existing.replace(
                    tzinfo=timezone.utc
                )

            if existing > now:
                now = existing

        except Exception:
            pass

    return now + timedelta(days=days)


async def activate_elite(
    user_id: int,
    plan_id: str,
    payment_id: Optional[str] = None,
) -> EliteResult:

    if not is_valid_plan(plan_id):
        return EliteResult(
            success=False,
            message="❌ Elite tarifi topilmadi.",
        )

    plan = get_plan(plan_id)

    if not plan:
        return EliteResult(
            success=False,
            message="❌ Elite tarifi topilmadi.",
        )

    creator = await is_creator(user_id)

    if creator:
        return EliteResult(
            success=True,
            plan_id=plan_id,
            message=(
                "𓆩 ELITE YARATUVCHI 𓆪\n\n"
                "⚜️ THRONE Elite siz uchun doimiy aktiv."
            ),
            data={
                "creator": True,
                "permanent": True,
            },
        )

    try:
        user = await get_user(user_id)

        current_expiry = None

        if user:
            current_expiry = user.get(
                "elite_expires_at"
            )

        expiry = calculate_expiry(
            plan["days"],
            current_expiry,
        )

        await execute(
            """
            UPDATE users
            SET elite_active = 1,
                elite_plan = ?,
                elite_expires_at = ?
            WHERE user_id = ?
            """,
            (
                plan_id,
                expiry.isoformat(),
                user_id,
            ),
        )

        return EliteResult(
            success=True,
            plan_id=plan_id,
            expires_at=expiry.isoformat(),
            message=(
                "⚜️ THRONE ELITE AKTIV!\n\n"
                f"📦 Tarif: {plan['name']}\n"
                f"📅 Amal qilish muddati: {plan['days']} kun\n"
                f"⏳ Tugash vaqti: {expiry.strftime('%Y-%m-%d %H:%M UTC')}"
            ),
            data={
                "plan": plan,
                "payment_id": payment_id,
                "expires_at": expiry.isoformat(),
            },
        )

    except Exception as exc:
        return EliteResult(
            success=False,
            message=f"❌ Elite aktivlashtirilmadi: {exc}",
        )


async def deactivate_expired_elite(
    user_id: int,
) -> EliteResult:

    if await is_creator(user_id):
        return EliteResult(
            success=True,
            message="𓆩 ELITE YARATUVCHI 𓆪 — Elite doimiy aktiv.",
        )

    try:
        await execute(
            """
            UPDATE users
            SET elite_active = 0
            WHERE user_id = ?
            """,
            (user_id,),
        )

        return EliteResult(
            success=True,
            message="⚜️ Elite muddati tugadi.",
        )

    except Exception as exc:
        return EliteResult(
            success=False,
            message=f"❌ Elite holatini yangilab bo‘lmadi: {exc}",
        )


async def check_and_update_elite(
    user_id: int,
) -> bool:

    if await is_creator(user_id):
        return True

    status = await get_elite_status(user_id)

    if status == ELITE_EXPIRED:
        await deactivate_expired_elite(user_id)
        return False

    return status == ELITE_ACTIVE


def get_plan_text(plan_id: str) -> str:
    plan = get_plan(plan_id)

    if not plan:
        return "❌ Tarif topilmadi."

    return (
        f"⚜️ {plan['name']}\n\n"
        f"📅 Muddat: {plan['days']} kun\n"
        f"💵 Narx: ${plan['price']:.2f}\n"
        f"💳 Valyuta: {plan['currency']}"
    )


def get_plans_text() -> str:
    lines = [
        "⚜️ THRONE ELITE",
        "",
        "Premium imkoniyatlardan foydalaning.",
        "",
    ]

    for plan_id, plan in ELITE_PLANS.items():
        lines.append(
            f"⚜️ {plan['name']} — "
            f"${plan['price']:.2f}"
        )

    lines.extend(
        [
            "",
            "👑 Creator uchun Elite:",
            "∞ DOIMIY AKTIV",
        ]
    )

    return "\n".join(lines)


def get_features_text() -> str:
    lines = [
        "⚜️ THRONE ELITE IMKONIYATLARI",
        "",
    ]

    for feature in ELITE_FEATURES:
        lines.append(feature)

    return "\n".join(lines)


async def get_elite_dashboard(
    user_id: int,
) -> str:

    if await is_creator(user_id):
        return (
            "𓆩 ELITE YARATUVCHI 𓆪\n\n"
            "⚜️ THRONE ELITE\n"
            "🟢 Holat: DOIMIY AKTIV\n"
            "♾️ Muddat: CHEKSIZ\n"
            "💎 Premium: AKTIV\n"
            "🎁 Elite bonuslari: AKTIV"
        )

    status = await get_elite_status(user_id)

    if status == ELITE_ACTIVE:
        try:
            user = await get_user(user_id)

            expiry = user.get(
                "elite_expires_at"
            ) if user else None

            plan_id = user.get(
                "elite_plan"
            ) if user else None

            plan = get_plan(plan_id) if plan_id else None

            plan_name = (
                plan["name"]
                if plan
                else "Elite"
            )

            return (
                "⚜️ THRONE ELITE\n\n"
                "🟢 Holat: AKTIV\n"
                f"📦 Tarif: {plan_name}\n"
                f"⏳ Tugash: {expiry or 'Noma’lum'}"
            )

        except Exception:
            return (
                "⚜️ THRONE ELITE\n\n"
                "🟢 Holat: AKTIV"
            )

    return (
        "⚜️ THRONE ELITE\n\n"
        "🔴 Holat: AKTIV EMAS\n\n"
        "Premium imkoniyatlarni ochish uchun "
        "Elite tariflaridan birini tanlang."
    )


def get_payment_payload(
    user_id: int,
    plan_id: str,
) -> Optional[dict]:

    plan = get_plan(plan_id)

    if not plan:
        return None

    return {
        "user_id": user_id,
        "plan_id": plan_id,
        "title": f"THRONE Elite — {plan['name']}",
        "description": (
            f"THRONE Elite premium obunasi — "
            f"{plan['days']} kun."
        ),
        "amount_usd": plan["price"],
        "currency": plan["currency"],
    }


def get_telegram_payment_amount(
    plan_id: str,
    currency: str = "USD",
) -> Optional[int]:

    plan = get_plan(plan_id)

    if not plan:
        return None

    if currency.upper() == "USD":
        return int(round(plan["price"] * 100))

    return None


async def confirm_payment(
    user_id: int,
    plan_id: str,
    payment_id: str,
) -> EliteResult:

    if not payment_id:
        return EliteResult(
            success=False,
            message="❌ To‘lov identifikatori topilmadi.",
        )

    return await activate_elite(
        user_id=user_id,
        plan_id=plan_id,
        payment_id=payment_id,
    )


def elite_benefit_multiplier(
    is_active: bool,
) -> float:
    return 1.25 if is_active else 1.0


def elite_daily_bonus(
    is_active: bool,
) -> int:
    return 500 if is_active else 0


def elite_ranking_bonus(
    is_active: bool,
) -> int:
    return 10 if is_active else 0


def elite_summary(
    is_active: bool,
) -> dict:

    return {
        "active": is_active,
        "benefit_multiplier": elite_benefit_multiplier(
            is_active
        ),
        "daily_bonus": elite_daily_bonus(
            is_active
        ),
        "ranking_bonus": elite_ranking_bonus(
            is_active
        ),
        "features": list(ELITE_FEATURES),
    }


def serialize_plan(plan_id: str) -> Optional[dict]:
    plan = get_plan(plan_id)

    if not plan:
        return None

    return {
        "id": plan_id,
        **plan,
    }


def serialize_all_plans() -> List[dict]:
    return [
        serialize_plan(plan_id)
        for plan_id in ELITE_PLANS
    ]


def elite_system_status() -> dict:
    return {
        "enabled": True,
        "plans": len(ELITE_PLANS),
        "features": len(ELITE_FEATURES),
        "creator_permanent": True,
        "payment_ready": True,
    }


def elite_system_text() -> str:
    status = elite_system_status()

    return (
        "⚜️ THRONE ELITE\n\n"
        f"Holat: {'AKTIV' if status['enabled'] else 'O‘CHIQ'}\n"
        f"Tariflar: {status['plans']}\n"
        f"Imkoniyatlar: {status['features']}\n"
        "👑 Creator Elite: DOIMIY\n"
        "💳 To‘lov tizimi: TAYYOR"
)
