from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

from database import (
    ensure_user, get_user, get_inventory, get_user_clan, list_clans, get_clan,
    clan_members, leave_clan_db,
)
from config import is_creator, ELITE_DIAMOND_PRICES, PAYMENT_PROVIDER_TOKEN
from keyboards import main_menu
from economy import balance, spend
from elite_system import active as elite_active, grant as elite_grant
from clan_system import create_clan, join_clan
from family_system import propose, accept
from duel_system import challenge, resolve
from black_market import ITEMS as BM_ITEMS, buy as bm_buy, list_text as bm_list_text
from economy_shop import ITEMS as SHOP_ITEMS, buy as shop_buy
from royal_system import court_text, my_position
from territory_system import territories
from language_system import LANGUAGES, set_language, get_language
from ai_system import answer as ai_answer
from tournament_system import create_tournament
from database import open_tournaments, join_tournament, tournament_players_list
from payment_system import create_elite_invoice, ELITE_STAR_PLANS, handle_pre_checkout, handle_successful_payment
from channel_system import list_text as channels_text, claim_reward
from territory_system import attack as territory_attack
from war_system import declare_war, attack_round, try_finish_war

router = Router()


def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ ORQAGA", callback_data="menu:back")]])


# ============================================================
# PROFILE / KINGDOM / INVENTORY
# ============================================================

@router.callback_query(F.data == "menu:profile")
async def cb_profile(c: CallbackQuery):
    u = await get_user(c.from_user.id)
    gold = "∞" if is_creator(c.from_user.id) else u["gold"]
    elite = "✅ AKTIV" if await elite_active(c.from_user.id) else "❌ Yo‘q"
    text = (f"👤 PROFIL\n\n{u['full_name']}\n🟡 Gold: {gold}\n🪙 Coin: {u['coin']}\n"
            f"💎 Diamond: {u['diamond']}\n⭐ Level: {u['level']}\n⚜️ Elite: {elite}")
    await c.message.edit_text(text, reply_markup=back_kb())
    await c.answer()


@router.callback_query(F.data == "menu:kingdom")
async def cb_kingdom(c: CallbackQuery):
    from kingdom import get_kingdom
    k = await get_kingdom(c.from_user.id)
    text = (f"🏰 {k['name']} {k['flag']}\n\n🟡 Xazina: {k['gold']}\n🛡️ Himoya: {k['defense']}\n"
            f"⚔️ Qo‘shin: {k['military']}\n⭐ Daraja: {k['level']}")
    await c.message.edit_text(text, reply_markup=back_kb())
    await c.answer()


@router.callback_query(F.data == "menu:inventory")
async def cb_inventory(c: CallbackQuery):
    items = await get_inventory(c.from_user.id)
    text = "🎒 INVENTAR\n\n" + ("\n".join(f"• {x['item_id']} ×{x['quantity']}" for x in items) if items else "Inventar bo‘sh.")
    await c.message.edit_text(text, reply_markup=back_kb())
    await c.answer()


@router.callback_query(F.data == "menu:missions")
async def cb_missions(c: CallbackQuery):
    await c.message.edit_text("🎯 MISSIYALAR\n\nHozircha faol missiya yo‘q. Tez orada qo‘shiladi.", reply_markup=back_kb())
    await c.answer()


# ============================================================
# SHOP
# ============================================================

def shop_kb():
    rows = [[InlineKeyboardButton(text=f"{v['name']} — {v['price']} {v['currency']}", callback_data=f"shop:buy:{k}")]
            for k, v in SHOP_ITEMS.items()]
    rows.append([InlineKeyboardButton(text="⬅️ ORQAGA", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu:shop")
async def cb_shop(c: CallbackQuery):
    await c.message.edit_text("💰 DO‘KON\n\nSotib olish uchun tanlang:", reply_markup=shop_kb())
    await c.answer()


@router.callback_query(F.data.startswith("shop:buy:"))
async def cb_shop_buy(c: CallbackQuery):
    item_id = c.data.split(":", 2)[2]
    ok = await shop_buy(c.from_user.id, item_id)
    await c.answer("✅ Sotib olindi!" if ok else "❌ Mablag‘ yetarli emas.", show_alert=True)


# ============================================================
# BLACK MARKET
# ============================================================

def bm_kb():
    rows = [[InlineKeyboardButton(text=f"{v[0]} — {v[1]} {v[2]}", callback_data=f"bm:buy:{k}")]
            for k, v in BM_ITEMS.items()]
    rows.append([InlineKeyboardButton(text="⬅️ ORQAGA", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu:blackmarket")
async def cb_blackmarket(c: CallbackQuery):
    await c.message.edit_text(bm_list_text(), reply_markup=bm_kb())
    await c.answer()


@router.callback_query(F.data.startswith("bm:buy:"))
async def cb_bm_buy(c: CallbackQuery):
    item_key = c.data.split(":", 2)[2]
    result = await bm_buy(c.from_user.id, item_key)
    if result["ok"]:
        await c.answer(f"✅ {result['name']} sotib olindi!", show_alert=True)
    else:
        await c.answer("❌ Mablag‘ yetarli emas yoki mahsulot topilmadi.", show_alert=True)


# ============================================================
# CLAN
# ============================================================

def clan_kb(in_clan):
    if in_clan:
        rows = [[InlineKeyboardButton(text="📋 A'ZOLAR", callback_data="clan:members")],
                [InlineKeyboardButton(text="🚪 CHIQISH", callback_data="clan:leave")]]
    else:
        rows = [[InlineKeyboardButton(text="🆕 KLAN YARATISH", callback_data="clan:create")],
                [InlineKeyboardButton(text="📜 KLANLAR RO‘YXATI", callback_data="clan:list")]]
    rows.append([InlineKeyboardButton(text="⬅️ ORQAGA", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu:clan")
async def cb_clan(c: CallbackQuery):
    clan = await get_user_clan(c.from_user.id)
    if clan:
        text = f"🏴 {clan['name']}\n\n{clan['description'] or '—'}\n⭐ Daraja: {clan['level']}\n💪 Kuch: {clan['power']}\n🎖️ Lavozim: {clan['position']}"
    else:
        text = "🏴 KLANIM\n\nSiz hozircha klanga a'zo emassiz."
    await c.message.edit_text(text, reply_markup=clan_kb(bool(clan)))
    await c.answer()


@router.callback_query(F.data == "clan:list")
async def cb_clan_list(c: CallbackQuery):
    clans = await list_clans()
    text = "📜 KLANLAR\n\n" + ("\n".join(f"• {cl['name']} (⭐{cl['level']})" for cl in clans) if clans else "Klanlar yo‘q.")
    await c.message.edit_text(text, reply_markup=back_kb())
    await c.answer()


@router.callback_query(F.data == "clan:members")
async def cb_clan_members(c: CallbackQuery):
    clan = await get_user_clan(c.from_user.id)
    if not clan:
        return await c.answer("Siz klanda emassiz.", show_alert=True)
    members = await clan_members(clan["clan_id"])
    text = "📋 A'ZOLAR\n\n" + "\n".join(f"• {m['full_name']} ({m['position']})" for m in members)
    await c.message.edit_text(text, reply_markup=back_kb())
    await c.answer()


@router.callback_query(F.data == "clan:leave")
async def cb_clan_leave(c: CallbackQuery):
    await leave_clan_db(c.from_user.id)
    await c.answer("Klandan chiqdingiz.", show_alert=True)


@router.callback_query(F.data == "clan:create")
async def cb_clan_create(c: CallbackQuery):
    await c.message.answer("Klan nomini yozing: /createclan NOM")
    await c.answer()
