# ============================================================
# THRONE — KEYBOARDS
# ============================================================

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


# ============================================================
# MAIN MENU
# ============================================================

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👤 KABINET"),
                KeyboardButton(text="🏰 QIROLLIGIM"),
            ],
            [
                KeyboardButton(text="🎒 INVENTAR"),
                KeyboardButton(text="💰 DO‘KON"),
            ],
            [
                KeyboardButton(text="🏴 KLANIM"),
                KeyboardButton(text="❤️ OILA"),
            ],
            [
                KeyboardButton(text="⚔️ KUCHLARIM"),
                KeyboardButton(text="🏆 MUSOBAQALAR"),
            ],
            [
                KeyboardButton(text="🎭 ROLLAR"),
                KeyboardButton(text="📊 REYTING"),
            ],
            [
                KeyboardButton(text="🎁 BONUSLAR"),
                KeyboardButton(text="🕶️ QORA BOZOR"),
            ],
            [
                KeyboardButton(text="⚜️ THRONE ELITE"),
                KeyboardButton(text="🌐 TIL"),
            ],
            [
                KeyboardButton(text="🤖 THRONE AI"),
                KeyboardButton(text="❓ YORDAM"),
            ],
            [
                KeyboardButton(text="⚙️ SOZLAMALAR"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="THRONE menyusidan tanlang...",
    )


# ============================================================
# BACK BUTTON
# ============================================================

def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ]
        ]
    )


# ============================================================
# CABINET
# ============================================================

def cabinet_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 STATISTIKA",
                    callback_data="cabinet_stats",
                ),
                InlineKeyboardButton(
                    text="🏅 YUTUQLAR",
                    callback_data="cabinet_achievements",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🪪 NIK",
                    callback_data="cabinet_nickname",
                ),
                InlineKeyboardButton(
                    text="🚩 BAYROQ",
                    callback_data="cabinet_flag",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎭 PROFIL KO‘RINISHI",
                    callback_data="cabinet_appearance",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# KINGDOM
# ============================================================

def kingdom_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏰 QAL’A",
                    callback_data="kingdom_castle",
                ),
                InlineKeyboardButton(
                    text="👑 TAХT",
                    callback_data="kingdom_throne",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⚔️ ARMIYA",
                    callback_data="kingdom_army",
                ),
                InlineKeyboardButton(
                    text="🗺️ XARITA",
                    callback_data="kingdom_map",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗺️ HUDUDLAR",
                    callback_data="kingdom_territory",
                ),
                InlineKeyboardButton(
                    text="⚔️ URUSHLAR",
                    callback_data="kingdom_wars",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# CASTLE
# ============================================================

def castle_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬆️ QAL’ANI RIVOJLANTIRISH",
                    callback_data="castle_upgrade",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛡️ HIMOYA",
                    callback_data="castle_defense",
                ),
                InlineKeyboardButton(
                    text="💰 XAZINA",
                    callback_data="castle_treasury",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 QO‘RIQCHILAR",
                    callback_data="castle_guards",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ QIROLLIGIM",
                    callback_data="kingdom_main",
                )
            ],
        ]
    )


# ============================================================
# THRONE
# ============================================================

def throne_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👑 HUKMDOR",
                    callback_data="throne_ruler",
                ),
                InlineKeyboardButton(
                    text="📜 FARMONLAR",
                    callback_data="throne_decrees",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏛️ SAROY",
                    callback_data="throne_court",
                ),
                InlineKeyboardButton(
                    text="⚖️ QARORLAR",
                    callback_data="throne_decisions",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ QIROLLIGIM",
                    callback_data="kingdom_main",
                )
            ],
        ]
    )


# ============================================================
# ARMY
# ============================================================

def army_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚔️ ASKARLAR",
                    callback_data="army_soldiers",
                ),
                InlineKeyboardButton(
                    text="🏹 KAMONCHILAR",
                    callback_data="army_archers",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🛡️ QO‘RIQCHILAR",
                    callback_data="army_guards",
                ),
                InlineKeyboardButton(
                    text="🐎 SUVARIYLAR",
                    callback_data="army_cavalry",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✨ MAXSUS QO‘SHIN",
                    callback_data="army_special",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ QIROLLIGIM",
                    callback_data="kingdom_main",
                )
            ],
        ]
    )


# ============================================================
# INVENTORY
# ============================================================

def inventory_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚔️ QUROLLAR",
                    callback_data="inventory_weapons",
                ),
                InlineKeyboardButton(
                    text="🛡️ ZIRHLAR",
                    callback_data="inventory_armor",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👕 KIYIMLAR",
                    callback_data="inventory_clothes",
                ),
                InlineKeyboardButton(
                    text="🐎 OTLAR",
                    callback_data="inventory_horses",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎁 SOVG‘ALAR",
                    callback_data="inventory_gifts",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# SHOP
# ============================================================

def shop_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚔️ QUROLLAR",
                    callback_data="shop_weapons",
                ),
                InlineKeyboardButton(
                    text="🛡️ ZIRHLAR",
                    callback_data="shop_armor",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👕 KIYIMLAR",
                    callback_data="shop_clothes",
                ),
                InlineKeyboardButton(
                    text="🐎 OTLAR",
                    callback_data="shop_horses",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎁 SOVG‘ALAR",
                    callback_data="shop_gifts",
                ),
                InlineKeyboardButton(
                    text="💎 PREMIUM",
                    callback_data="shop_premium",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# CLAN
# ============================================================

def clan_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏴 KLANIM",
                    callback_data="clan_profile",
                ),
                InlineKeyboardButton(
                    text="👥 A’ZOLAR",
                    callback_data="clan_members",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⚔️ KLAN URUSHI",
                    callback_data="clan_war",
                ),
                InlineKeyboardButton(
                    text="🏆 KLAN REYTINGI",
                    callback_data="clan_ranking",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💰 KLAN XAZINASI",
                    callback_data="clan_treasury",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔎 KLANLARNI QIDIRISH",
                    callback_data="clan_search",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# FAMILY
# ============================================================

def family_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❤️ OILAM",
                    callback_data="family_profile",
                ),
                InlineKeyboardButton(
                    text="📊 OILA STATISTIKASI",
                    callback_data="family_stats",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎁 OILA BONUSI",
                    callback_data="family_bonus",
                ),
                InlineKeyboardButton(
                    text="📜 TARIX",
                    callback_data="family_history",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# COMPETITIONS
# ============================================================

def competitions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏆 SOLO CHEMPIONATI",
                    callback_data="tournament_solo",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏴 KLAN CHEMPIONATI",
                    callback_data="tournament_clan",
                )
            ],
            [
                InlineKeyboardButton(
                    text="👑 THRONE CUP",
                    callback_data="tournament_throne",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚔️ DUEL",
                    callback_data="duel_menu",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 NATIJALAR",
                    callback_data="tournament_results",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# ROLES
# ============================================================

def roles_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👑 TAXT TOMONI",
                    callback_data="roles_taxt",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🩸 QORA TOMON",
                    callback_data="roles_qora",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏴 ISYON TOMONI",
                    callback_data="roles_isyon",
                )
            ],
            [
                InlineKeyboardButton(
                    text="☠️ MUSTAQIL",
                    callback_data="roles_independent",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📜 BARCHA ROLLAR",
                    callback_data="roles_all",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# REWARDS
# ============================================================

def rewards_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎁 KUNLIK BONUS",
                    callback_data="reward_daily",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏆 REYTING BONUSI",
                    callback_data="reward_ranking",
                ),
                InlineKeyboardButton(
                    text="🎁 SOVG‘ALAR",
                    callback_data="reward_gifts",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# BLACK MARKET
# ============================================================

def black_market_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🕶️ MAXSUS BUYUMLAR",
                    callback_data="black_items",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 NOYOB BUYUMLAR",
                    callback_data="black_rare",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚠️ YASHIRIN TAKLIFLAR",
                    callback_data="black_secret",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 YANGILASH",
                    callback_data="black_refresh",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# ELITE
# ============================================================

def elite_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚜️ ELITE HAQIDA",
                    callback_data="elite_info",
                )
            ],
            [
                InlineKeyboardButton(
                    text="7 KUN — $1",
                    callback_data="elite_buy_7",
                ),
                InlineKeyboardButton(
                    text="30 KUN — $3",
                    callback_data="elite_buy_30",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="90 KUN — $7",
                    callback_data="elite_buy_90",
                ),
                InlineKeyboardButton(
                    text="180 KUN — $12",
                    callback_data="elite_buy_180",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="365 KUN — $20",
                    callback_data="elite_buy_365",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ ORQAGA",
                    callback_data="back_main",
                )
            ],
        ]
    )


# ============================================================
# LANGUAGE
# ============================================================

def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
 
