import uuid
from aiogram.types import LabeledPrice
from config import ELITE_DIAMOND_PRICES
from database import create_payment, get_payment, complete_payment
from elite_system import grant

# Telegram Stars (XTR) narxlari — plan: (kunlar, yulduz narxi)
ELITE_STAR_PLANS = {
    "7d": (7, 150),
    "30d": (30, 500),
    "90d": (90, 1300),
    "180d": (180, 2200),
    "365d": (365, 3800),
}

async def create_elite_invoice(bot, chat_id, user_id, plan):
    info = ELITE_STAR_PLANS.get(plan)
    if not info:
        return None
    days, stars = info
    payload = f"elite:{plan}:{user_id}:{uuid.uuid4().hex[:8]}"
    await create_payment(user_id, payload, plan, stars, currency="XTR")
    await bot.send_invoice(
        chat_id=chat_id,
        title=f"THRONE Elite — {days} kun",
        description="Elite maqom sizga qo‘shimcha imkoniyatlar beradi.",
        payload=payload,
        currency="XTR",
        prices=[LabeledPrice(label=f"Elite {days} kun", amount=stars)],
        provider_token="",
    )
    return payload

async def handle_pre_checkout(pre_checkout_query):
    payment = await get_payment(pre_checkout_query.invoice_payload)
    if not payment or payment["status"] == "completed":
        await pre_checkout_query.answer(ok=False, error_message="To‘lov topilmadi yoki allaqachon amalga oshirilgan.")
        return
    await pre_checkout_query.answer(ok=True)

async def handle_successful_payment(message):
    sp = message.successful_payment
    payload = sp.invoice_payload
    payment = await get_payment(payload)
    if not payment:
        return None
    ok = await complete_payment(payload, sp.telegram_payment_charge_id)
    if not ok:
        return None
    plan = payment["plan"]
    days = ELITE_STAR_PLANS.get(plan, (0, 0))[0]
    await grant(payment["user_id"], days, payment["user_id"])
    return days
