from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from config import CREATOR_ID
from database import get_user, execute
from elite_system import (
    get_elite_plan,
    get_elite_status,
    activate_elite,
)


PAYMENT_PROVIDER = "telegram"

CURRENCY_USD = "USD"


@dataclass
class PaymentResult:
    success: bool
    message: str
    payment_id: Optional[str] = None
    user_id: Optional[int] = None
    plan_id: Optional[str] = None
    amount: float = 0.0
    currency: str = CURRENCY_USD
    data: Optional[Dict[str, Any]] = None


def is_creator(user_id: int) -> bool:
    return int(user_id) == int(CREATOR_ID)


def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    return get_elite_plan(plan_id)


def get_payment_amount(plan_id: str) -> int:
    """
    Telegram Payments uchun summa eng kichik birlikda saqlanadi.
    USD uchun cents:
    $1 = 100
    $3 = 300
    """
    plan = get_plan(plan_id)

    if not plan:
        return 0

    price = float(plan.get("price", 0))
    return int(round(price * 100))


def create_invoice_payload(
    user_id: int,
    plan_id: str,
) -> PaymentResult:
    if not plan_id:
        return PaymentResult(
            success=False,
            message="❌ Elite tarifi tanlanmagan.",
            user_id=user_id,
        )

    plan = get_plan(plan_id)

    if not plan:
        return PaymentResult(
            success=False,
            message="❌ Bunday Elite tarifi mavjud emas.",
            user_id=user_id,
            plan_id=plan_id,
        )

    if is_creator(user_id):
        return PaymentResult(
            success=True,
            message="👑 Yaratuchi uchun Elite doimiy aktiv.",
            user_id=user_id,
            plan_id=plan_id,
            amount=0,
            currency=CURRENCY_USD,
            data={
                "creator": True,
                "permanent": True,
                "plan_id": plan_id,
            },
        )

    amount = get_payment_amount(plan_id)

    if amount <= 0:
        return PaymentResult(
            success=False,
            message="❌ To‘lov summasi noto‘g‘ri.",
            user_id=user_id,
            plan_id=plan_id,
        )

    payload = {
        "type": "throne_elite",
        "user_id": int(user_id),
        "plan_id": plan_id,
        "amount": amount,
        "currency": CURRENCY_USD,
        "provider": PAYMENT_PROVIDER,
    }

    return PaymentResult(
        success=True,
        message="✅ To‘lov ma'lumotlari tayyor.",
        user_id=user_id,
        plan_id=plan_id,
        amount=amount / 100,
        currency=CURRENCY_USD,
        data=payload,
    )


def build_invoice_title(plan_id: str) -> str:
    plan = get_plan(plan_id)

    if not plan:
        return "THRONE ELITE"

    days = plan.get("days", 0)

    return f"THRONE ELITE — {days} kun"


def build_invoice_description(plan_id: str) -> str:
    plan = get_plan(plan_id)

    if not plan:
        return "THRONE ELITE"

    days = plan.get("days", 0)
    price = plan.get("price", 0)

    return (
        f"⚜️ THRONE ELITE\n\n"
        f"⏳ Muddat: {days} kun\n"
        f"💵 Narx: ${price}\n\n"
        f"👑 Elite imkoniyatlari avtomatik faollashadi."
    )


async def save_payment(
    user_id: int,
    payment_id: str,
    plan_id: str,
    amount: float,
    currency: str = CURRENCY_USD,
    status: str = "paid",
) -> bool:
    if not payment_id:
        return False

    try:
        await execute(
            """
            INSERT INTO elite_purchases
            (user_id, plan_id, amount, currency, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(user_id),
                plan_id,
                float(amount),
                currency,
                status,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        return True

    except Exception:
        return False


async def confirm_elite_payment(
    user_id: int,
    payment_id: str,
    plan_id: str,
    amount: float,
    currency: str = CURRENCY_USD,
) -> PaymentResult:

    if not payment_id:
        return PaymentResult(
            success=False,
            message="❌ To‘lov ID topilmadi.",
            user_id=user_id,
            plan_id=plan_id,
        )

    if not plan_id or not get_plan(plan_id):
        return PaymentResult(
            success=False,
            message="❌ Elite tarifi topilmadi.",
            user_id=user_id,
            plan_id=plan_id,
        )

    if amount <= 0:
        return PaymentResult(
            success=False,
            message="❌ To‘lov summasi noto‘g‘ri.",
            user_id=user_id,
            plan_id=plan_id,
        )

    expected_amount = float(get_plan(plan_id).get("price", 0))

    if round(float(amount), 2) != round(expected_amount, 2):
        return PaymentResult(
            success=False,
            message="❌ To‘lov summasi Elite tarifiga mos kelmaydi.",
            user_id=user_id,
            plan_id=plan_id,
            amount=amount,
            currency=currency,
        )

    saved = await save_payment(
        user_id=user_id,
        payment_id=payment_id,
        plan_id=plan_id,
        amount=amount,
        currency=currency,
        status="paid",
    )

    if not saved:
        return PaymentResult(
            success=False,
            message="❌ To‘lovni saqlashda xatolik yuz berdi.",
            user_id=user_id,
            plan_id=plan_id,
        )

    try:
        activated = await activate_elite(
            user_id=user_id,
            plan_id=plan_id,
        )
    except Exception:
        activated = False

    if not activated:
        return PaymentResult(
            success=False,
            message="⚠️ To‘lov qabul qilindi, ammo Elite faollashtirishda xatolik yuz berdi.",
            payment_id=payment_id,
            user_id=user_id,
            plan_id=plan_id,
            amount=amount,
            currency=currency,
        )

    return PaymentResult(
        success=True,
        message=(
            "⚜️ THRONE ELITE FAOLLASHDI!\n\n"
            f"👑 Tarif: {plan_id}\n"
            f"💵 To‘lov: ${amount:.2f}\n"
            "✨ Elite imkoniyatlari endi faol."
        ),
        payment_id=payment_id,
        user_id=user_id,
        plan_id=plan_id,
        amount=amount,
        currency=currency,
    )


async def get_payment_history(
    user_id: int,
    limit: int = 20,
):
    limit = max(1, min(int(limit), 100))

    try:
        from database import fetchall

        return await fetchall(
            """
            SELECT *
            FROM elite_purchases
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(user_id), limit),
        )
    except Exception:
        return []


async def get_payment(
    payment_id: str,
):
    if not payment_id:
        return None

    try:
        from database import fetchone

        return await fetchone(
            """
            SELECT *
            FROM elite_purchases
            WHERE payment_id = ?
            LIMIT 1
            """,
            (payment_id,),
        )
    except Exception:
        return None


async def refund_payment(
    user_id: int,
    payment_id: str,
) -> PaymentResult:

    if not is_creator(user_id):
        return PaymentResult(
            success=False,
            message="❌ Bu amal faqat yaratuvchi uchun.",
            user_id=user_id,
        )

    if not payment_id:
        return PaymentResult(
            success=False,
            message="❌ Payment ID kerak.",
            user_id=user_id,
        )

    try:
        await execute(
            """
            UPDATE elite_purchases
            SET status = 'refunded'
            WHERE payment_id = ?
            """,
            (payment_id,),
        )

        return PaymentResult(
            success=True,
            message="✅ To‘lov refund sifatida belgilandi.",
            payment_id=payment_id,
            user_id=user_id,
        )

    except Exception as e:
        return PaymentResult(
            success=False,
            message=f"❌ Refund xatosi: {e}",
            payment_id=payment_id,
            user_id=user_id,
        )


def payment_system_status() -> Dict[str, Any]:
    return {
        "system": "THRONE Payment System",
        "provider": PAYMENT_PROVIDER,
        "currency": CURRENCY_USD,
        "elite_payment": True,
        "automatic_activation": True,
        "creator_free_elite": True,
    }


def payment_system_text() -> str:
    return (
        "💳 THRONE PAYMENT\n\n"
        "⚜️ Elite real pul orqali sotib olinadi.\n"
        "⚡ To‘lov tasdiqlangach Elite avtomatik faollashadi.\n"
        "👑 Yaratuchi uchun Elite doimiy va bepul.\n\n"
        "🔐 To‘lovlar THRONE tizimi orqali qayd etiladi."
    )


def serialize_payment_result(result: PaymentResult) -> Dict[str, Any]:
    return {
        "success": result.success,
        "message": result.message,
        "payment_id": result.payment_id,
        "user_id": result.user_id,
        "plan_id": result.plan_id,
        "amount": result.amount,
        "currency": result.currency,
        "data": result.data,
    }


def validate_payment_amount(
    plan_id: str,
    amount: float,
    currency: str = CURRENCY_USD,
) -> bool:
    if currency != CURRENCY_USD:
        return False

    plan = get_plan(plan_id)

    if not plan:
        return False

    expected = float(plan.get("price", 0))

    return round(float(amount), 2) == round(expected, 2)
