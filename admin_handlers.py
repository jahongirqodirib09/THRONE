from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import is_creator
from database import get_user
from elite_system import grant

router=Router()

@router.message(Command("giveelite"))
async def giveelite(m:Message):
    if not is_creator(m.from_user.id):
        return await m.answer("⛔ Bu buyruq faqat creator uchun.")
    parts=m.text.split()
    if len(parts)!=3:return await m.answer("Foydalanish: /giveelite USER_ID KUN")
    try: uid=int(parts[1]); days=int(parts[2])
    except:return await m.answer("USER_ID va kun soni raqam bo‘lishi kerak.")
    if not await get_user(uid):return await m.answer("❌ Foydalanuvchi topilmadi.")
    await grant(uid,days,m.from_user.id)
    await m.answer(f"⚜️ Elite {days} kunga berildi.")

from royal_system import crown_king, appoint, dismiss, POSITIONS
from tournament_system import create_tournament
from database import add_channel


@router.message(Command("crown"))
async def crown_cmd(m: Message):
    if not is_creator(m.from_user.id):
        return await m.answer("⛔ Bu buyruq faqat creator uchun.")
    parts = m.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await m.answer("Foydalanish: /crown USER_ID")
    uid = int(parts[1])
    if not await get_user(uid):
        return await m.answer("❌ Foydalanuvchi topilmadi.")
    await crown_king(uid)
    await m.answer("👑 Yangi Shoh tayinlandi.")


@router.message(Command("appoint"))
async def appoint_cmd(m: Message):
    if not is_creator(m.from_user.id):
        return await m.answer("⛔ Bu buyruq faqat creator uchun.")
    parts = m.text.split(maxsplit=2)
    if len(parts) != 3:
        return await m.answer("Foydalanish: /appoint USER_ID LAVOZIM\nLavozimlar: " + ", ".join(POSITIONS))
    uid, position = parts[1], parts[2]
    if not uid.isdigit():
        return await m.answer("USER_ID raqam bo‘lishi kerak.")
    ok = await appoint(position, int(uid))
    await m.answer("✅ Tayinlandi." if ok else "❌ Noto‘g‘ri lavozim nomi.")


@router.message(Command("dismiss"))
async def dismiss_cmd(m: Message):
    if not is_creator(m.from_user.id):
        return await m.answer("⛔ Bu buyruq faqat creator uchun.")
    parts = m.text.split(maxsplit=1)
    if len(parts) != 2:
        return await m.answer("Foydalanish: /dismiss LAVOZIM")
    ok = await dismiss(parts[1])
    await m.answer("✅ Lavozimdan olindi." if ok else "❌ Noto‘g‘ri lavozim nomi.")


@router.message(Command("createtournament"))
async def create_tournament_cmd(m: Message):
    if not is_creator(m.from_user.id):
        return await m.answer("⛔ Bu buyruq faqat creator uchun.")
    parts = m.text.split(maxsplit=1)
    if len(parts) != 2:
        return await m.answer("Foydalanish: /createtournament NOM")
    tid = await create_tournament(parts[1].strip())
    await m.answer(f"🏆 Musobaqa yaratildi. ID: {tid}")


@router.message(Command("addchannel"))
async def add_channel_cmd(m: Message):
    if not is_creator(m.from_user.id):
        return await m.answer("⛔ Bu buyruq faqat creator uchun.")
    parts = m.text.split(maxsplit=3)
    if len(parts) < 3 or not parts[1].lstrip("-").isdigit():
        return await m.answer("Foydalanish: /addchannel CHANNEL_ID REWARD_GOLD [NOM]")
    channel_id, reward = int(parts[1]), int(parts[2])
    title = parts[3] if len(parts) > 3 else ""
    await add_channel(channel_id, title=title, reward_gold=reward, required=False)
    await m.answer("✅ Kanal qo‘shildi.")
