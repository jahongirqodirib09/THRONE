# ============================================================
# THRONE — ECONOMY SYSTEM
# ============================================================

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from config import CREATOR_ID
from database import (
    get_user,
    update_balance,
    spend_balance,
    get_daily_reward,
    update_daily_reward,
)


# ============================================================
# CURRENCIES
# ============================================================

GOLD = "gold"
COIN = "coin"
DIAMOND = "diamond"


# ============================================================
# DAILY REWARD
# ============================================================

DAILY_GOLD = 500
DAILY_COIN = 10
DAILY_DIAMOND = 1


# ============================================================
# TRANSFER LIMITS
# ============================================================

MIN_TRANSFER_GOLD = 1
MAX_TRANSFER_GOLD = 1_000_000


# ============================================================
# RESULT
# ============================================================

@dataclass
class EconomyResult:
    success: bool
    message: str
    amount: int = 0


# ============================================================
# CREATOR CHECK
# ============================================================

def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


# ============================================================
# VALID CURRENCY
# ============================================================

def is_valid_currency(currency: str) -> bool:
    return currency in {
        GOLD,
        COIN,
        DIAMOND,
    }


# ============================================================
# CURRENCY NAME
# ============================================================

def currency_name(currency: str) -> str:

    names = {
        GOLD: "🟡 Oltin",
        COIN: "🪙 Coin",
        DIAMOND: "💎 Olmos",
    }

    return names.get(
        currency,
        "Noma’lum",
    )


# ============================================================
# CREATOR BALANCE
# ============================================================

def creator_balance(
    user_id: int,
    currency: str,
):
    if is_creator(user_id):
        return float("inf")

    return None


# ============================================================
# GET BALANCE
# ============================================================

async def get_balance(
    user_id: int,
    currency: str,
) -> int:

    if not is_valid_currency(currency):
        return 0

    if is_creator(user_id):
        return float("inf")

    user = await get_user(user_id)

    if not user:
        return 0

    return int(
        user.get(
            currency,
            0,
        )
        or 0
    )


# ============================================================
# BALANCE TEXT
# ============================================================

async def get_wallet_text(
    user_id: int,
) -> str:

    if is_creator(user_id):
        return (
            "💰 HAMYON\n\n"
            "🟡 Oltin: ∞\n"
            "🪙 Coin: ∞\n"
            "💎 Olmos: ∞\n"
            "⚜️ Elite Pass: AKTIV ∞"
        )

    gold = await get_balance(
        user_id,
        GOLD,
    )

    coin = await get_balance(
        user_id,
        COIN,
    )

    diamond = await get_balance(
        user_id,
        DIAMOND,
    )

    return (
        "💰 HAMYON\n\n"
        f"🟡 Oltin: {gold:,}\n"
        f"🪙 Coin: {coin:,}\n"
        f"💎 Olmos: {diamond:,}"
    )


# ============================================================
# ADD BALANCE
# ============================================================

async def add_currency(
    user_id: int,
    currency: str,
    amount: int,
) -> EconomyResult:

    if not is_valid_currency(currency):
        return EconomyResult(
            False,
            "❌ Noto‘g‘ri valyuta.",
        )

    if amount <= 0:
        return EconomyResult(
            False,
            "❌ Miqdor 0 dan katta bo‘lishi kerak.",
        )

    if is_creator(user_id):
        return EconomyResult(
            True,
            "♾️ Creator resurslari cheksiz.",
            amount,
        )

    try:
        await update_balance(
            user_id,
            currency,
            amount,
        )

        return EconomyResult(
            True,
            f"✅ {amount:,} "
            f"{currency_name(currency)} qo‘shildi.",
            amount,
        )

    except Exception as exc:
        return EconomyResult(
            False,
            f"❌ Balansni yangilashda xatolik: {exc}",
        )


# ============================================================
# SPEND BALANCE
# ============================================================

async def spend_currency(
    user_id: int,
    currency: str,
    amount: int,
) -> EconomyResult:

    if not is_valid_currency(currency):
        return EconomyResult(
            False,
            "❌ Noto‘g‘ri valyuta.",
        )

    if amount <= 0:
        return EconomyResult(
            False,
            "❌ Miqdor 0 dan katta bo‘lishi kerak.",
        )

    # Creator uchun xarajat cheksiz resurs sabab
    # real balans kamaytirilmaydi.
    if is_creator(user_id):
        return EconomyResult(
            True,
            "♾️ Creator uchun xarid tasdiqlandi.",
            amount,
        )

    try:
        result = await spend_balance(
            user_id,
            currency,
            amount,
        )

        if not result:
            return EconomyResult(
                False,
                f"❌ Yetarli {currency_name(currency)} mavjud emas.",
            )

        return EconomyResult(
            True,
            f"✅ {amount:,} "
            f"{currency_name(currency)} sarflandi.",
            amount,
        )

    except Exception as exc:
        return EconomyResult(
            False,
            f"❌ To‘lovda xatolik: {exc}",
        )


# ============================================================
# TRANSFER GOLD
# ============================================================

async def transfer_gold(
    sender_id: int,
    receiver_id: int,
    amount: int,
) -> EconomyResult:

    if sender_id == receiver_id:
        return EconomyResult(
            False,
            "❌ O‘zingizga oltin yubora olmaysiz.",
        )

    if amount < MIN_TRANSFER_GOLD:
        return EconomyResult(
            False,
            f"❌ Minimal transfer: {MIN_TRANSFER_GOLD} oltin.",
        )

    if amount > MAX_TRANSFER_GOLD:
        return EconomyResult(
            False,
            f"❌ Maksimal transfer: {MAX_TRANSFER_GOLD:,} oltin.",
        )

    receiver = await get_user(receiver_id)

    if not receiver:
        return EconomyResult(
            False,
            "❌ Qabul qiluvchi o‘yinchi topilmadi.",
        )

    result = await spend_currency(
        sender_id,
        GOLD,
        amount,
    )

    if not result.success:
        return result

    added = await add_currency(
        receiver_id,
        GOLD,
        amount,
    )

    if not added.success:
        # Creator bo‘lmagan yuboruvchidan yechilgan
        # mablag‘ni qaytarishga harakat qilamiz.
        if not is_creator(sender_id):
            await add_currency(
                sender_id,
                GOLD,
                amount,
            )

        return EconomyResult(
            False,
            "❌ Transfer yakunlanmadi.",
        )

    return EconomyResult(
        True,
        f"🟡 {amount:,} oltin yuborildi.",
        amount,
    )


# ============================================================
# GIFT
# ============================================================

async def send_gift(
    sender_id: int,
    receiver_id: int,
    amount: int,
    gift_name: str = "🎁 Sovg‘a",
) -> EconomyResult:

    if sender_id == receiver_id:
        return EconomyResult(
            False,
            "❌ O‘zingizga sovg‘a yubora olmaysiz.",
        )

    if amount <= 0:
        return EconomyResult(
            False,
            "❌ Sovg‘a qiymati noto‘g‘ri.",
        )

    receiver = await get_user(receiver_id)

    if not receiver:
        return EconomyResult(
            False,
            "❌ Qabul qiluvchi topilmadi.",
        )

    result = await spend_currency(
        sender_id,
        GOLD,
        amount,
    )

    if not result.success:
        return result

    added = await add_currency(
        receiver_id,
        GOLD,
        amount,
    )

    if not added.success:

        if not is_creator(sender_id):
            await add_currency(
                sender_id,
                GOLD,
                amount,
            )

        return EconomyResult(
            False,
            "❌ Sovg‘ani yuborishda xatolik.",
        )

    return EconomyResult(
        True,
        f"🎁 {gift_name} yuborildi.",
        amount,
    )


# ============================================================
# DAILY REWARD
# ============================================================

async def claim_daily(
    user_id: int,
) -> EconomyResult:

    # Creator uchun daily bonus cheksiz.
    if is_creator(user_id):
        return EconomyResult(
            True,
            (
                "🎁 DAILY BONUS\n\n"
                "𓆩 ELITE YARATUVCHI 𓆪\n\n"
                "🟡 Oltin: ∞\n"
                "🪙 Coin: ∞\n"
                "💎 Olmos: ∞"
            ),
        )

    try:
        reward = await get_daily_reward(
            user_id
        )
    except Exception:
        reward = None

    now = datetime.now(
        timezone.utc
    )

    # Database mavjud ma’lumot qaytarsa,
    # oxirgi claim vaqtini tekshiramiz.
    if reward:
        last_claim = (
            reward.get("last_claim")
            or reward.get("claimed_at")
            or reward.get("updated_at")
        )

        if last_claim:
            try:
                last_dt = datetime.fromisoformat(
                    str(last_claim).replace(
                        "Z",
                        "+00:00",
                    )
                )

                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(
                        tzinfo=timezone.utc
                    )

                seconds = (
                    now - last_dt
                ).total_seconds()

                if seconds < 86400:
                    remaining = int(
                        86400 - seconds
                    )

                    hours = remaining // 3600
                    minutes = (
                        remaining % 3600
                    ) // 60

                    return EconomyResult(
                        False,
                        (
                            "⏳ Kunlik bonus "
                            "hali olinmagan.\n\n"
                            f"Qolgan vaqt: "
                            f"{hours}s {minutes}daq."
                        ),
                    )

            except (
                ValueError,
                TypeError,
            ):
                pass

    # Mukofot berish
    await add_currency(
        user_id,
        GOLD,
        DAILY_GOLD,
    )

    await add_currency(
        user_id,
        COIN,
        DAILY_COIN,
    )

    await add_currency(
        user_id,
        DIAMOND,
        DAILY_DIAMOND,
    )

    # Database helper mavjud bo‘lsa,
    # daily holatini saqlashga uriniladi.
    try:
        await update_daily_reward(
            user_id,
            now.isoformat(),
        )
    except TypeError:
        try:
            await update_daily_reward(
                user_id
            )
        except Exception:
            pass
    except Exception:
        pass

    return EconomyResult(
        True,
        (
            "🎁 KUNLIK BONUS OLINDI!\n\n"
            f"🟡 +{DAILY_GOLD:,} Oltin\n"
            f"🪙 +{DAILY_COIN} Coin\n"
            f"💎 +{DAILY_DIAMOND} Olmos"
        ),
    )


# ============================================================
# SHOP PURCHASE
# ============================================================

async def purchase(
    user_id: int,
    price: int,
    currency: str = GOLD,
) -> EconomyResult:

    if price <= 0:
        return EconomyResult(
            False,
            "❌ Mahsulot narxi noto‘g‘ri.",
        )

    return await spend_currency(
        user_id,
        currency,
        price,
    )


# ============================================================
# REWARD
# ============================================================

async def give_reward(
    user_id: int,
    gold: int = 0,
    coin: int = 0,
    diamond: int = 0,
) -> EconomyResult:

    if gold < 0 or coin < 0 or diamond < 0:
        return EconomyResult(
            False,
            "❌ Mukofot miqdori noto‘g‘ri.",
        )

    if gold:
        await add_currency(
            user_id,
            GOLD,
            gold,
        )

    if coin:
        await add_currency(
            user_id,
            COIN,
            coin,
        )

    if diamond:
        await add_currency(
            user_id,
            DIAMOND,
            diamond,
        )

    return EconomyResult(
        True,
        "🎁 Mukofot berildi.",
    )


# ============================================================
# FORMAT BALANCE
# ============================================================

def format_amount(
    amount,
) -> str:

    if amount == float("inf"):
        return "∞"

    return f"{int(amount):,}"


# ============================================================
# ECONOMY SUMMARY
# ============================================================

async def economy_summary(
    user_id: int,
) -> dict:

    return {
        "gold": await get_balance(
            user_id,
            GOLD,
        ),
        "coin": await get_balance(
            user_id,
            COIN,
        ),
        "diamond": await get_balance(
            user_id,
            DIAMOND,
        ),
        "elite": is_creator(user_id),
    }


# ============================================================
# CREATOR ECONOMY CHECK
# ============================================================

def creator_has_unlimited(
    user_id: int,
) -> bool:

    return is_creator(user_id)
