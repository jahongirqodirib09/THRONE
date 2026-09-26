import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from config import CREATOR_ID
from database import fetchall

from inactivity_system import check_inactivity
from elite_system import get_elite_status


logger = logging.getLogger("THRONE.SCHEDULER")


# ============================================================
# THRONE SCHEDULER
# ============================================================

CHECK_INTERVAL = 3600          # har 1 soatda
INACTIVITY_INTERVAL = 3600     # har 1 soatda
ELITE_INTERVAL = 3600          # har 1 soatda


_scheduler_task: Optional[asyncio.Task] = None
_running = False


# ============================================================
# USERS
# ============================================================

async def get_all_user_ids():
    try:
        rows = await fetchall(
            """
            SELECT user_id
            FROM users
            """
        )

        result = []

        for row in rows or []:
            try:
                if isinstance(row, dict):
                    user_id = row.get("user_id")
                else:
                    user_id = row[0]

                if user_id:
                    result.append(int(user_id))

            except Exception:
                continue

        return result

    except Exception as e:
        logger.error("Foydalanuvchilarni olishda xatolik: %s", e)
        return []


# ============================================================
# INACTIVITY CHECK
# ============================================================

async def run_inactivity_check():
    user_ids = await get_all_user_ids()

    checked = 0
    warnings = 0
    inactive = 0

    for user_id in user_ids:

        if user_id == CREATOR_ID:
            continue

        try:
            result = await check_inactivity(user_id)

            checked += 1

            if result.should_warn:
                warnings += 1

                logger.info(
                    "Inactivity warning: user=%s days=%s",
                    user_id,
                    result.days_inactive,
                )

            if result.should_remove:
                inactive += 1

                logger.info(
                    "Inactive user detected: user=%s days=%s",
                    user_id,
                    result.days_inactive,
                )

        except Exception as e:
            logger.error(
                "Inactivity check xatosi user=%s: %s",
                user_id,
                e,
            )

    return {
        "checked": checked,
        "warnings": warnings,
        "inactive": inactive,
    }


# ============================================================
# ELITE CHECK
# ============================================================

async def run_elite_check():
    user_ids = await get_all_user_ids()

    checked = 0
    active = 0
    expired = 0

    for user_id in user_ids:

        if user_id == CREATOR_ID:
            continue

        try:
            status = await get_elite_status(user_id)

            checked += 1

            if isinstance(status, dict):
                is_active = bool(
                    status.get("active")
                    or status.get("elite_active")
                )
            else:
                is_active = bool(status)

            if is_active:
                active += 1

        except Exception as e:
            logger.error(
                "Elite check xatosi user=%s: %s",
                user_id,
                e,
            )

    return {
        "checked": checked,
        "active": active,
        "expired": expired,
    }


# ============================================================
# DAILY TASK
# ============================================================

async def run_daily_tasks():
    """
    Kunlik tizimlar uchun markaziy joy.
    Keyinchalik ranking, bonus va channel postlar shu yerga ulanadi.
    """

    logger.info("THRONE daily tasks ishga tushdi.")

    return {
        "success": True,
        "time": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# HOURLY TASK
# ============================================================

async def run_hourly_tasks():
    inactivity = await run_inactivity_check()
    elite = await run_elite_check()

    logger.info(
        "THRONE hourly check | inactivity=%s | elite=%s",
        inactivity,
        elite,
    )

    return {
        "inactivity": inactivity,
        "elite": elite,
    }


# ============================================================
# SCHEDULER LOOP
# ============================================================

async def scheduler_loop():
    global _running

    _running = True

    logger.info("THRONE Scheduler ishga tushdi.")

    last_daily_date = None

    while _running:

        try:
            now = datetime.now(timezone.utc)
            current_date = now.date()

            # ------------------------------------------------
            # DAILY
            # ------------------------------------------------

            if last_daily_date != current_date:

                try:
                    await run_daily_tasks()
                    last_daily_date = current_date

                except Exception as e:
                    logger.error(
                        "Daily task xatosi: %s",
                        e,
                    )

            # ------------------------------------------------
            # HOURLY
            # ------------------------------------------------

            try:
                await run_hourly_tasks()

            except Exception as e:
                logger.error(
                    "Hourly task xatosi: %s",
                    e,
                )

        except asyncio.CancelledError:
            logger.info("THRONE Scheduler bekor qilindi.")
            break

        except Exception as e:
            logger.error(
                "Scheduler loop xatosi: %s",
                e,
            )

        await asyncio.sleep(CHECK_INTERVAL)

    _running = False

    logger.info("THRONE Scheduler to'xtadi.")


# ============================================================
# START
# ============================================================

async def start_scheduler():
    global _scheduler_task

    if _scheduler_task is not None:
        if not _scheduler_task.done():
            return _scheduler_task

    _scheduler_task = asyncio.create_task(
        scheduler_loop()
    )

    logger.info("THRONE Scheduler task yaratildi.")

    return _scheduler_task


# ============================================================
# STOP
# ============================================================

async def stop_scheduler():
    global _scheduler_task
    global _running

    _running = False

    if _scheduler_task is None:
        return

    if not _scheduler_task.done():

        _scheduler_task.cancel()

        try:
            await _scheduler_task

        except asyncio.CancelledError:
            pass

    _scheduler_task = None

    logger.info("THRONE Scheduler to'xtatildi.")


# ============================================================
# STATUS
# ============================================================

def scheduler_status():
    running = (
        _scheduler_task is not None
        and not _scheduler_task.done()
    )

    return {
        "system": "THRONE Scheduler",
        "running": running,
        "check_interval": CHECK_INTERVAL,
        "inactivity_interval": INACTIVITY_INTERVAL,
        "elite_interval": ELITE_INTERVAL,
    }


# ============================================================
# MANUAL CHECK
# ============================================================

async def run_manual_check():
    """
    Creator/admin tomonidan qo'lda ishga tushirish uchun.
    """

    inactivity = await run_inactivity_check()
    elite = await run_elite_check()

    return {
        "success": True,
        "inactivity": inactivity,
        "elite": elite,
        "time": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# SYSTEM TEXT
# ============================================================

def scheduler_text():
    status = scheduler_status()

    return (
        "⏱️ <b>THRONE SCHEDULER</b>\n\n"
        f"🔄 Holat: "
        f"<b>{'AKTIV' if status['running'] else 'TO‘XTAGAN'}</b>\n"
        f"⏰ Tekshiruv: <b>har 1 soatda</b>\n"
        "⚠️ Inactivity: <b>AKTIV</b>\n"
        "⚜️ Elite nazorati: <b>AKTIV</b>\n"
        "🎁 Daily tizimi: <b>AKTIV</b>"
          )
