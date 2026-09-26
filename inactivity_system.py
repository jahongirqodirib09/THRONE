from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from config import CREATOR_ID
from database import (
    get_inactivity,
    update_activity,
)


# ============================================================
# THRONE INACTIVITY SYSTEM
# ============================================================

WARNING_AFTER_DAYS = 7
REMOVE_AFTER_DAYS = 14

STATUS_ACTIVE = "active"
STATUS_WARNING = "warning"
STATUS_INACTIVE = "inactive"
STATUS_PROTECTED = "protected"


@dataclass
class InactivityResult:
    success: bool
    status: str
    message: str
    user_id: int
    days_inactive: int = 0
    last_activity: Optional[str] = None
    should_warn: bool = False
    should_remove: bool = False


def is_creator(user_id: int) -> bool:
    return int(user_id) == int(CREATOR_ID)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None

    if isinstance(value, datetime):
        dt = value
    else:
        try:
            text = str(value).replace("Z", "+00:00")
            dt = datetime.fromisoformat(text)
        except (ValueError, TypeError):
            return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def calculate_days_inactive(last_activity: Any) -> int:
    dt = parse_datetime(last_activity)

    if not dt:
        return 0

    seconds = max(0, (utc_now() - dt).total_seconds())

    return int(seconds // 86400)


def get_inactivity_status(days_inactive: int) -> str:
    if days_inactive >= REMOVE_AFTER_DAYS:
        return STATUS_INACTIVE

    if days_inactive >= WARNING_AFTER_DAYS:
        return STATUS_WARNING

    return STATUS_ACTIVE


async def mark_activity(user_id: int) -> InactivityResult:
    """
    Foydalanuvchi botga kirganida faollikni yangilaydi.
    """

    if is_creator(user_id):
        return InactivityResult(
            success=True,
            status=STATUS_PROTECTED,
            message="👑 Creator akkaunti himoyalangan.",
            user_id=user_id,
        )

    now = utc_now().isoformat()

    try:
        await update_activity(
            user_id,
            now,
        )

        return InactivityResult(
            success=True,
            status=STATUS_ACTIVE,
            message="✅ Faollik yangilandi.",
            user_id=user_id,
            days_inactive=0,
            last_activity=now,
        )

    except Exception as e:
        return InactivityResult(
            success=False,
            status=STATUS_ACTIVE,
            message=f"❌ Faollikni yangilashda xatolik: {e}",
            user_id=user_id,
        )


async def check_inactivity(user_id: int) -> InactivityResult:
    """
    Bitta foydalanuvchining faol yoki faol emasligini tekshiradi.
    """

    if is_creator(user_id):
        return InactivityResult(
            success=True,
            status=STATUS_PROTECTED,
            message="👑 Creator akkaunti inactivity tizimidan himoyalangan.",
            user_id=user_id,
        )

    try:
        data = await get_inactivity(user_id)
    except Exception as e:
        return InactivityResult(
            success=False,
            status=STATUS_ACTIVE,
            message=f"❌ Inactivity ma'lumotini olishda xatolik: {e}",
            user_id=user_id,
        )

    if not data:
        result = await mark_activity(user_id)

        return InactivityResult(
            success=result.success,
            status=STATUS_ACTIVE,
            message="✅ Yangi foydalanuvchi sifatida faollik boshlandi.",
            user_id=user_id,
            days_inactive=0,
            last_activity=utc_now().isoformat(),
        )

    if isinstance(data, dict):
        last_activity = (
            data.get("last_activity")
            or data.get("last_seen")
            or data.get("updated_at")
            or data.get("activity_at")
        )
    else:
        try:
            last_activity = data["last_activity"]
        except Exception:
            last_activity = None

    days = calculate_days_inactive(last_activity)
    status = get_inactivity_status(days)

    if status == STATUS_INACTIVE:
        return InactivityResult(
            success=True,
            status=STATUS_INACTIVE,
            message=(
                "🚫 Faoliyatsizlik muddati tugagan.\n\n"
                f"⏳ Faol bo‘lmagan vaqt: {days} kun."
            ),
            user_id=user_id,
            days_inactive=days,
            last_activity=str(last_activity) if last_activity else None,
            should_remove=True,
        )

    if status == STATUS_WARNING:
        remaining = max(0, REMOVE_AFTER_DAYS - days)

        return InactivityResult(
            success=True,
            status=STATUS_WARNING,
            message=(
                "⚠️ THRONE FAOLLIK OGOHLANTIRISHI\n\n"
                f"⏳ Siz {days} kundan beri faol emassiz.\n"
                f"🚨 Hisobingiz cheklanishigacha: {remaining} kun.\n\n"
                "👑 THRONE’ga qaytib kiring va faollikni davom ettiring."
            ),
            user_id=user_id,
            days_inactive=days,
            last_activity=str(last_activity) if last_activity else None,
            should_warn=True,
        )

    return InactivityResult(
        success=True,
        status=STATUS_ACTIVE,
        message="✅ Foydalanuvchi faol.",
        user_id=user_id,
        days_inactive=days,
        last_activity=str(last_activity) if last_activity else None,
    )


async def get_inactivity_message(user_id: int) -> str:
    result = await check_inactivity(user_id)
    return result.message


async def should_remove_user(user_id: int) -> bool:
    if is_creator(user_id):
        return False

    result = await check_inactivity(user_id)

    return result.should_remove


async def should_warn_user(user_id: int) -> bool:
    if is_creator(user_id):
        return False

    result = await check_inactivity(user_id)

    return result.should_warn


async def get_days_until_removal(user_id: int) -> int:
    if is_creator(user_id):
        return -1

    result = await check_inactivity(user_id)

    if result.status == STATUS_INACTIVE:
        return 0

    return max(0, REMOVE_AFTER_DAYS - result.days_inactive)


async def process_user_activity(user_id: int) -> Dict[str, Any]:
    """
    Botga har qanday qayta kirishda ishlatiladi.
    """

    if is_creator(user_id):
        return {
            "success": True,
            "protected": True,
            "status": STATUS_PROTECTED,
            "user_id": user_id,
        }

    result = await mark_activity(user_id)

    return {
        "success": result.success,
        "protected": False,
        "status": result.status,
        "user_id": user_id,
        "last_activity": result.last_activity,
    }


async def process_inactivity_check(user_id: int) -> Dict[str, Any]:
    """
    Background scheduler keyinchalik shu funksiyadan foydalanishi mumkin.
    """

    result = await check_inactivity(user_id)

    return {
        "success": result.success,
        "status": result.status,
        "user_id": user_id,
        "days_inactive": result.days_inactive,
        "should_warn": result.should_warn,
        "should_remove": result.should_remove,
        "message": result.message,
    }


def inactivity_settings() -> Dict[str, Any]:
    return {
        "warning_after_days": WARNING_AFTER_DAYS,
        "remove_after_days": REMOVE_AFTER_DAYS,
        "creator_protected": True,
        "automatic_warning": True,
        "automatic_inactivity_check": True,
    }


def inactivity_system_text() -> str:
    return (
        "⏱️ THRONE FAOLLIK TIZIMI\n\n"
        f"⚠️ Ogohlantirish: {WARNING_AFTER_DAYS} kun\n"
        f"🚫 Cheklash: {REMOVE_AFTER_DAYS} kun\n\n"
        "🔄 Botga qayta kirilganda faollik avtomatik yangilanadi.\n"
        "👑 Creator akkaunti himoyalangan."
    )


def serialize_result(result: InactivityResult) -> Dict[str, Any]:
    return {
        "success": result.success,
        "status": result.status,
        "message": result.message,
        "user_id": result.user_id,
        "days_inactive": result.days_inactive,
        "last_activity": result.last_activity,
        "should_warn": result.should_warn,
        "should_remove": result.should_remove,
      }
