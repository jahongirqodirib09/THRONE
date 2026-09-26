# ============================================================
# THRONE — SECURITY SYSTEM
# ============================================================

from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime, timezone
import hashlib
import hmac
import os
import secrets

from config import CREATOR_ID
from database import (
    security_log,
    get_user,
)


# ============================================================
# CONSTANTS
# ============================================================

ACTION_LOGIN = "login"
ACTION_ADMIN = "admin"
ACTION_BALANCE = "balance"
ACTION_PURCHASE = "purchase"
ACTION_TRANSFER = "transfer"
ACTION_GAME = "game"
ACTION_PROFILE = "profile"
ACTION_SECURITY = "security"
ACTION_TOKEN = "token"
ACTION_SYSTEM = "system"

LEVEL_INFO = "info"
LEVEL_WARNING = "warning"
LEVEL_CRITICAL = "critical"

MAX_TRANSFER_GOLD = 1_000_000
MAX_DAILY_TRANSFERS = 100

MAX_FAILED_ACTIONS = 10

SESSION_LENGTH = 32


# ============================================================
# RESULT
# ============================================================

@dataclass
class SecurityResult:
    success: bool
    message: str
    data: Optional[dict] = None


# ============================================================
# CREATOR
# ============================================================

def is_creator(user_id: int) -> bool:
    return int(user_id) == int(CREATOR_ID)


# ============================================================
# TIME
# ============================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# SAFE INTEGER
# ============================================================

def safe_int(
    value: Any,
    default: int = 0,
) -> int:

    try:
        return int(value)
    except (
        TypeError,
        ValueError,
    ):
        return default


# ============================================================
# USER VALIDATION
# ============================================================

async def validate_user(
    user_id: int,
) -> SecurityResult:

    user_id = safe_int(
        user_id
    )

    if user_id <= 0:
        return SecurityResult(
            False,
            "❌ Noto‘g‘ri foydalanuvchi ID.",
        )

    user = await get_user(
        user_id
    )

    if not user:
        return SecurityResult(
            False,
            "❌ Foydalanuvchi topilmadi.",
        )

    return SecurityResult(
        True,
        "✅ Foydalanuvchi tasdiqlandi.",
        {
            "user": user,
        },
    )


# ============================================================
# ADMIN VALIDATION
# ============================================================

def validate_creator(
    user_id: int,
) -> SecurityResult:

    if is_creator(
        user_id
    ):
        return SecurityResult(
            True,
            "✅ Creator tasdiqlandi.",
            {
                "creator": True,
            },
        )

    return SecurityResult(
        False,
        "⛔ Bu amal faqat creator uchun.",
        {
            "creator": False,
        },
    )


# ============================================================
# ADMIN ACTION PROTECTION
# ============================================================

def can_execute_admin_action(
    user_id: int,
    action: str,
) -> SecurityResult:

    if not is_creator(
        user_id
    ):
        return SecurityResult(
            False,
            "⛔ Ruxsat yo‘q.",
            {
                "authorized": False,
                "action": action,
            },
        )

    return SecurityResult(
        True,
        "✅ Amalga ruxsat berildi.",
        {
            "authorized": True,
            "action": action,
        },
    )


# ============================================================
# SECURITY LOG
# ============================================================

async def log_security_event(
    user_id: int,
    action: str,
    level: str = LEVEL_INFO,
    details: Optional[str] = None,
) -> SecurityResult:

    try:

        await security_log(
            user_id,
            action,
            level,
            details,
        )

        return SecurityResult(
            True,
            "✅ Xavfsizlik hodisasi yozildi.",
            {
                "user_id": user_id,
                "action": action,
                "level": level,
                "time": utc_now(),
            },
        )

    except TypeError:

        try:

            await security_log(
                user_id,
                action,
            )

            return SecurityResult(
                True,
                "✅ Xavfsizlik logi yozildi.",
            )

        except Exception as exc:

            return SecurityResult(
                False,
                "❌ Security log yozilmadi.",
                {
                    "error": str(exc),
                },
            )

    except Exception as exc:

        return SecurityResult(
            False,
            "❌ Security log xatosi.",
            {
                "error": str(exc),
            },
        )


# ============================================================
# SENSITIVE DATA DETECTION
# ============================================================

SENSITIVE_WORDS = (
    "token",
    "bot_token",
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "private_key",
)


def contains_sensitive_data(
    text: Optional[str],
) -> bool:

    if not text:
        return False

    value = str(
        text
    ).lower()

    return any(
        word in value
        for word in SENSITIVE_WORDS
    )


# ============================================================
# TOKEN MASKING
# ============================================================

def mask_secret(
    value: Optional[str],
) -> str:

    if not value:
        return ""

    value = str(
        value
    )

    if len(value) <= 8:
        return "*" * len(
            value
        )

    return (
        value[:4]
        + "..."
        + value[-4:]
    )


# ============================================================
# BOT TOKEN CHECK
# ============================================================

def token_security_check() -> SecurityResult:

    token = os.getenv(
        "BOT_TOKEN",
        "",
    ).strip()

    if not token:
        return SecurityResult(
            False,
            "❌ BOT_TOKEN mavjud emas.",
        )

    if len(token) < 20:
        return SecurityResult(
            False,
            "⚠️ BOT_TOKEN uzunligi shubhali.",
        )

    return SecurityResult(
        True,
        "✅ BOT_TOKEN Environment Variable orqali mavjud.",
        {
            "masked": mask_secret(
                token
            ),
        },
    )


# ============================================================
# CREATOR ID CHECK
# ============================================================

def creator_security_check() -> SecurityResult:

    creator_id = os.getenv(
        "CREATOR_ID",
        "",
    ).strip()

    if not creator_id:
        return SecurityResult(
            False,
            "❌ CREATOR_ID mavjud emas.",
        )

    try:
        value = int(
            creator_id
        )
    except ValueError:
        return SecurityResult(
            False,
            "❌ CREATOR_ID noto‘g‘ri.",
        )

    if value <= 0:
        return SecurityResult(
            False,
            "❌ CREATOR_ID noto‘g‘ri.",
        )

    return SecurityResult(
        True,
        "✅ CREATOR_ID sozlangan.",
        {
            "creator_id": value,
        },
    )


# ============================================================
# ENVIRONMENT SECURITY
# ============================================================

def environment_security_check() -> dict:

    token_check = token_security_check()
    creator_check = creator_security_check()

    return {
        "bot_token": {
            "ok": token_check.success,
            "message": token_check.message,
        },
        "creator_id": {
            "ok": creator_check.success,
            "message": creator_check.message,
        },
        "secure": (
            token_check.success
            and creator_check.success
        ),
    }


# ============================================================
# TRANSFER VALIDATION
# ============================================================

def validate_transfer(
    sender_id: int,
    receiver_id: int,
    amount: int,
) -> SecurityResult:

    sender_id = safe_int(
        sender_id
    )

    receiver_id = safe_int(
        receiver_id
    )

    amount = safe_int(
        amount
    )

    if sender_id <= 0:
        return SecurityResult(
            False,
            "❌ Yuboruvchi noto‘g‘ri.",
        )

    if receiver_id <= 0:
        return SecurityResult(
            False,
            "❌ Qabul qiluvchi noto‘g‘ri.",
        )

    if sender_id == receiver_id:
        return SecurityResult(
            False,
            "❌ O‘zingizga yubora olmaysiz.",
        )

    if amount <= 0:
        return SecurityResult(
            False,
            "❌ Miqdor 0 dan katta bo‘lishi kerak.",
        )

    if amount > MAX_TRANSFER_GOLD:
        return SecurityResult(
            False,
            "⛔ Transfer limiti oshib ketdi.",
            {
                "maximum": MAX_TRANSFER_GOLD,
            },
        )

    return SecurityResult(
        True,
        "✅ Transfer xavfsizlik tekshiruvidan o‘tdi.",
        {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount,
        },
    )


# ============================================================
# PURCHASE VALIDATION
# ============================================================

def validate_purchase(
    user_id: int,
    item_id: str,
    price: int,
) -> SecurityResult:

    user_id = safe_int(
        user_id
    )

    price = safe_int(
        price
    )

    if user_id <= 0:
        return SecurityResult(
            False,
            "❌ Noto‘g‘ri foydalanuvchi.",
        )

    if not item_id:
        return SecurityResult(
            False,
            "❌ Buyum ID mavjud emas.",
        )

    if price <= 0:
        return SecurityResult(
            False,
            "❌ Noto‘g‘ri narx.",
        )

    if price > 100_000_000:
        return SecurityResult(
            False,
            "⛔ Narx xavfsizlik chegarasidan oshdi.",
        )

    return SecurityResult(
        True,
        "✅ Xarid xavfsizlik tekshiruvidan o‘tdi.",
        {
            "user_id": user_id,
            "item_id": item_id,
            "price": price,
        },
    )


# ============================================================
# BALANCE CHANGE VALIDATION
# ============================================================

def validate_balance_change(
    user_id: int,
    amount: int,
    currency: str,
) -> SecurityResult:

    user_id = safe_int(
        user_id
    )

    amount = safe_int(
        amount
    )

    allowed_currencies = {
        "gold",
        "coin",
        "diamond",
    }

    if user_id <= 0:
        return SecurityResult(
            False,
            "❌ Noto‘g‘ri foydalanuvchi.",
        )

    if currency not in allowed_currencies:
        return SecurityResult(
            False,
            "❌ Noma’lum valyuta.",
        )

    if amount == 0:
        return SecurityResult(
            False,
            "❌ Balans o‘zgarishi 0 bo‘lishi mumkin emas.",
        )

    # Oddiy o‘yinchi uchun juda katta o‘zgarish
    # shubhali deb belgilanadi.
    if (
        not is_creator(user_id)
        and abs(amount) > 100_000_000
    ):
        return SecurityResult(
            False,
            "⛔ Balans o‘zgarishi xavfsizlik chegarasidan oshdi.",
        )

    return SecurityResult(
        True,
        "✅ Balans o‘zgarishi tekshirildi.",
        {
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
        },
    )


# ============================================================
# GAME ACTION VALIDATION
# ============================================================

def validate_game_action(
    user_id: int,
    game_id: int,
    action: str,
) -> SecurityResult:

    user_id = safe_int(
        user_id
    )

    game_id = safe_int(
        game_id
    )

    if user_id <= 0:
        return SecurityResult(
            False,
            "❌ O‘yinchi ID noto‘g‘ri.",
        )

    if game_id <= 0:
        return SecurityResult(
            False,
            "❌ O‘yin ID noto‘g‘ri.",
        )

    if not action:
        return SecurityResult(
            False,
            "❌ Amal ko‘rsatilmagan.",
        )

    return SecurityResult(
        True,
        "✅ O‘yin amali qabul qilindi.",
        {
            "user_id": user_id,
            "game_id": game_id,
            "action": action,
        },
    )


# ============================================================
# RANDOM SESSION ID
# ============================================================

def generate_session_id() -> str:

    return secrets.token_urlsafe(
        SESSION_LENGTH
    )


# ============================================================
# NONCE
# ============================================================

def generate_nonce() -> str:

    return secrets.token_hex(
        24
    )


# ============================================================
# REQUEST SIGNATURE
# ============================================================

def create_signature(
    payload: str,
    secret: str,
) -> str:

    if not payload:
        return ""

    if not secret:
        return ""

    return hmac.new(
        secret.encode(
            "utf-8"
        ),
        payload.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()


def verify_signature(
    payload: str,
    signature: str,
    secret: str,
) -> bool:

    if not payload:
        return False

    if not signature:
        return False

    if not secret:
        return False

    expected = create_signature(
        payload,
        secret,
    )

    return hmac.compare_digest(
        expected,
        signature,
    )


# ============================================================
# MINI APP DATA VALIDATION
# ============================================================

def validate_mini_app_data(
    user_id: int,
    data: Optional[dict],
) -> SecurityResult:

    user_id = safe_int(
        user_id
    )

    if user_id <= 0:
        return SecurityResult(
            False,
            "❌ Noto‘g‘ri user ID.",
        )

    if not isinstance(
        data,
        dict,
    ):
        return SecurityResult(
            False,
            "❌ Mini App ma’lumoti noto‘g‘ri.",
        )

    data_user_id = safe_int(
        data.get(
            "user_id",
            0,
        )
    )

    if data_user_id != user_id:
        return SecurityResult(
            False,
            "⛔ Mini App user ID mos kelmadi.",
        )

    return SecurityResult(
        True,
        "✅ Mini App ma’lumotlari tekshirildi.",
    )


# ============================================================
# ANTI-SPAM
# ============================================================

@dataclass
class RateLimitState:
    user_id: int
    action: str
    count: int = 0
    window_start: float = 0.0


_RATE_LIMITS = {}


def rate_limit_key(
    user_id: int,
    action: str,
) -> str:

    return f"{user_id}:{action}"


def check_rate_limit(
    user_id: int,
    action: str,
    maximum: int = 20,
    window_seconds: int = 60,
) -> SecurityResult:

    import time

    user_id = safe_int(
        user_id
    )

    key = rate_limit_key(
        user_id,
        action,
    )

    now = time.time()

    state = _RATE_LIMITS.get(
        key
    )

    if not state:

        state = RateLimitState(
            user_id=user_id,
            action=action,
            count=0,
            window_start=now,
        )

        _RATE_LIMITS[key] = state

    if (
        now
        - state.window_start
        >= window_seconds
    ):

        state.count = 0
        state.window_start = now

    state.count += 1

    if state.count > maximum:

        return SecurityResult(
            False,
            "⛔ Juda ko‘p so‘rov yuborildi. Biroz kuting.",
            {
                "action": action,
                "count": state.count,
                "maximum": maximum,
            },
        )

    return SecurityResult(
        True,
        "✅ So‘rov qabul qilindi.",
        {
            "count": state.count,
            "remaining": maximum - state.count,
        },
    )


# ============================================================
# SUSPICIOUS ACTION
# ============================================================

def suspicious_action(
    amount: int = 0,
    repeated: int = 0,
    unauthorized: bool = False,
) -> bool:

    if unauthorized:
        return True

    if abs(
        safe_int(amount)
    ) > 100_000_000:
        return True

    if repeated >= MAX_FAILED_ACTIONS:
        return True

    return False


# ============================================================
# SECURITY EVENT
# ============================================================

async def report_suspicious_action(
    user_id: int,
    action: str,
    reason: str,
) -> SecurityResult:

    return await log_security_event(
        user_id=user_id,
        action=action,
        level=LEVEL_WARNING,
        details=reason,
    )


# ============================================================
# CRITICAL SECURITY EVENT
# ============================================================

async def report_critical_event(
    user_id: int,
    action: str,
    reason: str,
) -> SecurityResult:

    return await log_security_event(
        user_id=user_id,
        action=action,
        level=LEVEL_CRITICAL,
        details=reason,
    )


# ============================================================
# SECURITY DASHBOARD
# ============================================================

def security_dashboard() -> dict:

    environment = environment_security_check()

    return {
        "environment": environment,
        "limits": {
            "max_transfer_gold": MAX_TRANSFER_GOLD,
            "max_daily_transfers": MAX_DAILY_TRANSFERS,
            "max_failed_actions": MAX_FAILED_ACTIONS,
        },
        "protections": {
            "creator_access": True,
            "balance_validation": True,
            "transfer_validation": True,
            "purchase_validation": True,
            "game_action_validation": True,
            "mini_app_validation": True,
            "rate_limit": True,
            "security_logs": True,
            "secret_masking": True,
            "request_signatures": True,
        },
    }


# ============================================================
# SECURITY SUMMARY
# ============================================================

def security_summary() -> str:

    data = security_dashboard()

    environment = data[
        "environment"
    ]

    status = (
        "🟢 XAVFSIZLIK ASOSIY TEKSHIRUVI OK"
        if environment["secure"]
        else
        "🟠 XAVFSIZLIK SOZLAMALARINI TEKSHIRISH KERAK"
    )

    return "\n".join(
        [
            "🛡️ THRONE SECURITY",
            "",
            status,
            "",
            "🔐 Creator nazorati: AKTIV",
            "💰 Balans tekshiruvi: AKTIV",
            "💸 Transfer tekshiruvi: AKTIV",
            "🛒 Xarid tekshiruvi: AKTIV",
            "🎮 O‘yin amallari: AKTIV",
            "📱 Mini App tekshiruvi: AKTIV",
            "🚦 Rate limit: AKTIV",
            "📝 Security log: AKTIV",
            "🔑 Secret masking: AKTIV",
            "🔏 Signature check: AKTIV",
        ]
    )


# ===============
