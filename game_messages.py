# ============================================================
# THRONE — GAME MESSAGES
# ============================================================

from typing import Any, Dict, List, Optional


# ============================================================
# BASIC HELPERS
# ============================================================

def player_name(player: Any) -> str:
    if isinstance(player, dict):
        return (
            player.get("name")
            or player.get("username")
            or str(player.get("user_id", "O'yinchi"))
        )

    return (
        getattr(player, "name", None)
        or getattr(player, "username", None)
        or str(getattr(player, "user_id", "O'yinchi"))
    )


def player_id(player: Any) -> Optional[int]:
    if isinstance(player, dict):
        value = player.get("user_id")
    else:
        value = getattr(player, "user_id", None)

    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def role_name(player: Any) -> str:
    if isinstance(player, dict):
        return player.get("role_name") or player.get("role_key") or "Noma'lum"

    return (
        getattr(player, "role_name", None)
        or getattr(player, "role_key", None)
        or "Noma'lum"
    )


# ============================================================
# LOBBY
# ============================================================

def lobby_message(
    game_id: int,
    players: List[Any],
    min_players: int = 7,
    max_players: int = 35,
) -> str:

    count = len(players)

    lines = [
        "👑 THRONE — O'YIN LOBBISI",
        "",
        f"🎮 O'yin: #{game_id}",
        f"👥 O'yinchilar: {count}/{max_players}",
        "",
    ]

    if count < min_players:
        lines.append(
            f"⏳ O'yinni boshlash uchun kamida {min_players} "
            f"nafar o'yinchi kerak."
        )
    else:
        lines.append(
            "✅ O'yinni boshlash uchun yetarli o'yinchi yig'ildi."
        )

    lines.extend(
        [
            "",
            "⚔️ Har bir o'yinchi o'z taqdirini yashirin rol bilan boshlaydi.",
            "👑 Taxt uchun kurashga tayyor bo'ling.",
        ]
    )

    return "\n".join(lines)


def player_list_message(
    players: List[Any],
) -> str:

    if not players:
        return (
            "👥 O'YINCHILAR\n\n"
            "Hozircha hech kim o'yinga qo'shilmagan."
        )

    lines = [
        "👥 O'YINCHILAR",
        "",
    ]

    for index, player in enumerate(players, start=1):
        lines.append(
            f"{index}. {player_name(player)}"
        )

    return "\n".join(lines)


def lobby_full_message(
    max_players: int = 35,
) -> str:

    return (
        "⚠️ O'YIN LOBBISI TO'LDI\n\n"
        f"👥 Maksimal o'yinchi soni: {max_players}\n"
        "❌ Yangi o'yinchi qo'shila olmaydi."
    )


def join_message(
    player: Any,
    count: int,
    max_players: int = 35,
) -> str:

    return (
        "👑 THRONE\n\n"
        f"⚔️ {player_name(player)} o'yinga qo'shildi.\n\n"
        f"👥 O'yinchilar: {count}/{max_players}"
    )


def leave_message(
    player: Any,
    count: int,
) -> str:

    return (
        "👑 THRONE\n\n"
        f"🚪 {player_name(player)} o'yinni tark etdi.\n\n"
        f"👥 Qolgan o'yinchilar: {count}"
    )


# ============================================================
# GAME START
# ============================================================

def game_start_message(
    players_count: int,
) -> str:

    return (
        "👑 THRONE — O'YIN BOSHLANDI\n\n"
        f"👥 O'yinchilar: {players_count}\n\n"
        "🎭 Rollar yashirin tarzda taqsimlanmoqda...\n"
        "🏰 Qirollik taqdiri hal qilinmoqda.\n\n"
        "⚔️ Har bir qaror o'yin taqdirini o'zgartirishi mumkin."
    )


def role_received_message(
    role: Any,
) -> str:

    if isinstance(role, dict):
        name = role.get("name", "Noma'lum rol")
        side = role.get("side", "Noma'lum")
        description = role.get("description", "")
        ability = role.get("ability", "")
        limitation = role.get("limitation", "")
        win = role.get("win", "")
    else:
        name = getattr(role, "name", "Noma'lum rol")
        side = getattr(role, "side", "Noma'lum")
        description = getattr(role, "description", "")
        ability = getattr(role, "ability", "")
        limitation = getattr(role, "limitation", "")
        win = getattr(role, "win", "")

    lines = [
        "🎭 THRONE — SIZNING ROLINGIZ",
        "",
        f"🎭 Rol: {name}",
        f"⚔️ Tomon: {side}",
        "",
    ]

    if description:
        lines.extend(
            [
                "📖 Vazifa:",
                description,
                "",
            ]
        )

    if ability:
        lines.extend(
            [
                "✨ Qobiliyat:",
                ability,
                "",
            ]
        )

    if limitation:
        lines.extend(
            [
                "⛓️ Cheklov:",
                limitation,
                "",
            ]
        )

    if win:
        lines.extend(
            [
                "🏆 G'alaba sharti:",
                win,
            ]
        )

    return "\n".join(lines)


# ============================================================
# NIGHT
# ============================================================

def night_start_message(
    night_number: int,
) -> str:

    return (
        "🌙 THRONE — TUN\n\n"
        f"🌑 {night_number}-tun boshlandi.\n\n"
        "🏰 Qirollik uyquga ketdi.\n"
        "🕵️ Yashirin harakatlar boshlanmoqda.\n\n"
        "⚔️ Har bir qaror tongda o'z ta'sirini ko'rsatadi."
    )


def night_waiting_message() -> str:

    return (
        "🌙 Tun davom etmoqda...\n\n"
        "🕯️ Qirollikdagi yashirin kuchlar harakatda."
    )


def night_action_received_message() -> str:

    return (
        "🌙 Tungi harakatingiz qabul qilindi.\n\n"
        "🔒 Nishoningiz boshqa o'yinchilarga ko'rsatilmaydi."
    )


def night_action_already_done_message() -> str:

    return (
        "⚠️ Tungi harakatingiz allaqachon yuborilgan."
    )


def night_action_blocked_message() -> str:

    return (
        "⛓️ Sizning harakatingiz bloklangan.\n\n"
        "🌑 Bu tun boshqa harakat qila olmaysiz."
    )


# ============================================================
# ACTION ATMOSPHERE
# ============================================================

def night_atmosphere(action_type: str) -> str:

    messages = {
        "observe": (
            "🕵️ Tun zulmatida kimdir yashirin kuzatuv olib bordi."
        ),
        "protect": (
            "🛡️ Qirollikning bir nuqtasi tun davomida himoya qilindi."
        ),
        "block": (
            "⛓️ Tun qorong'usida kimningdir yo'li to'sildi."
        ),
        "poison": (
            "☠️ Saroy atrofida zahar izlari sezildi."
        ),
        "weaken": (
            "🩸 Kimdir tun davomida kuchini yo'qotdi."
        ),
        "attack": (
            "⚔️ Tun sukunatini yashirin hujum ovozi buzdi."
        ),
        "special": (
            "✨ Qirollikda noma'lum kuch harakatga keldi."
        ),
    }

    return messages.get(
        action_type,
        "🌑 Tun davomida noma'lum voqea yuz berdi.",
    )


# ============================================================
# MORNING
# ============================================================

def morning_message(
    deaths: Optional[List[Any]] = None,
) -> str:

    deaths = deaths or []

    lines = [
        "🌅 THRONE — TONG",
        "",
        "☀️ Yangi kun boshlandi.",
        "",
    ]

    if not deaths:
        lines.extend(
            [
                "🛡️ Bu tun hech kim o'ldirilmadi.",
                "🏰 Qirollik omon qoldi.",
            ]
        )

        return "\n".join(lines)

    if len(deaths) == 1:
        lines.append(
            "☠️ Bu tun bir o'yinchi o'yinni tark etdi."
        )
    else:
        lines.append(
            f"☠️ Bu tun {len(deaths)} nafar o'yinchi o'yinni tark etdi."
        )

    lines.append("")

    for dead in deaths:
        lines.append(
            f"☠️ {player_name(dead)}"
        )

    lines.extend(
        [
            "",
            "⚔️ Endi qirollikda muhokama boshlanadi.",
        ]
    )

    return "\n".join(lines)


# ============================================================
# DISCUSSION
# ============================================================

def discussion_message(
    seconds: int = 120,
) -> str:

    return (
        "💬 THRONE — MUHOKAMA\n\n"
        "🏰 Qirollik kengashi yig'ildi.\n\n"
        "🗣️ O'yinchilar o'z fikrlarini bildirishlari mumkin.\n"
        "🔎 Shubhali harakatlarni muhokama qiling.\n\n"
        f"⏱️ Muhokama vaqti: {seconds} soniya\n\n"
        "⚠️ Eslab qoling: har bir ayblov keyingi qarorga ta'sir qilishi mumkin."
    )


def discussion_ended_message() -> str:

    return (
        "⏰ MUHOKAMA YAKUNLANDI\n\n"
        "⚖️ Endi qirollik hukmi uchun ovoz berish boshlanadi."
    )


# ============================================================
# VOTING
# ============================================================

def voting_message(
    players: List[Any],
    seconds: int = 60,
) -> str:

    lines = [
        "⚖️ THRONE — OVOZ BERISH",
        "",
        "🏰 Qirollik kengashi hukm chiqaradi.",
        "",
        f"⏱️ Ovoz berish vaqti: {seconds} soniya",
        "",
        "👥 Nomzodlar:",
    ]

    for index, player in enumerate(players, start=1):
        lines.append(
            f"{index}. {player_name(player)}"
        )

    lines.extend(
        [
            "",
            "⚠️ O'z ovozingizni ehtiyotkorlik bilan bering.",
        ]
    )

    return "\n".join(lines)


def vote_received_message() -> str:

    return (
        "⚖️ Ovozingiz qabul qilindi.\n\n"
        "🔒 Sizning tanlovingiz yashirin saqlanadi."
    )


def vote_already_cast_message() -> str:

    return (
        "⚠️ Siz allaqachon ovoz bergansiz."
    )


def vote_result_message(
    eliminated: Optional[Any] = None,
    tied: bool = False,
    no_elimination: bool = False,
) -> str:

    if tied:
        return (
            "⚖️ OVOZ NATIJASI\n\n"
            "🤝 Ovozlar teng chiqdi.\n\n"
            "🔄 Qayta ovoz berish boshlanadi."
        )

    if no_elimination:
        return (
            "⚖️ OVOZ NATIJASI\n\n"
            "🤝 Ovozlar yana teng chiqdi.\n\n"
            "🕊️ Bu safar hech kim chiqarilmadi."
        )

    if eliminated is None:
        return (
            "⚖️ OVOZ NATIJASI\n\n"
            "🕊️ Hech kim o'yindan chiqarilmadi."
        )

    return (
        "⚖️ OVOZ NATIJASI\n\n"
        f"☠️ {player_name(eliminated)} "
        "o'yindan chiqarildi.\n\n"
        "🕯️ Uning so'nggi so'zi uchun vaqt beriladi."
    )


# ============================================================
# LAST WORDS
# ============================================================

def last_words_message(
    player: Any,
    seconds: int = 30,
) -> str:

    return (
        "🕯️ THRONE — SO'NGGI SO'Z\n\n"
        f"☠️ {player_name(player)} o'yindan chiqarildi.\n\n"
        "🎙️ Endi unga so'nggi fikrlarini bildirish imkoniyati beriladi.\n\n"
        f"⏱️ Vaqt: {seconds} soniya"
    )


def last_words_received_message() -> str:

    return (
        "🕯️ So'nggi so'zingiz qabul qilindi."
    )


def auto_last_words_message(
    player: Any,
) -> str:

    return (
        "🕯️ SO'NGGI SO'Z\n\n"
        f"☠️ {player_name(player)} jim qoldi.\n\n"
        "🌑 THRONE tarixida uning nomi qoldi."
    )


# ============================================================
# ELIMINATION
# ============================================================

def elimination_message(
    player: Any,
    reveal_role: bool = True,
) -> str:

    lines = [
        "☠️ THRONE — ELIMINATSIYA",
        "",
        f"☠️ {player_name(player)} o'yinni tark etdi.",
    ]

    if reveal_role:
        lines.extend(
            [
                "",
                f"🎭 Roli: {role_name(player)}",
            ]
        )

    return "\n".join(lines)


# ============================================================
# PLAYER LEFT
# ============================================================

def player_eliminated_private_message(
    player: Any,
) -> str:

    return (
        "☠️ THRONE\n\n"
        "Siz o'yindan chiqarildingiz.\n\n"
        "🏰 Siz endi tirik o'yinchilar orasida "
        "harakat qila olmaysiz.\n\n"
        "📜 Ammo o'yin tarixidagi izingiz saqlanadi."
    )


# ============================================================
# GAME STOP
# ============================================================

def game_stopped_message(
    reason: str = "O'yin administrator tomonidan to'xtatildi.",
) -> str:

    return (
        "🛑 THRONE — O'YIN TO'XTATILDI\n\n"
        f"⚠️ {reason}\n\n"
        "🏰 Ushbu o'yin yakunlandi."
    )


# ============================================================
# GAME FINISHED
# ============================================================

def game_finished_message(
    winner_name: str,
    winners: Optional[List[Any]] = None,
    reason: str = "",
) -> str:

    winners = winners or []

    lines = [
        "👑 THRONE — O'YIN YAKUNLANDI",
        "",
        f"🏆 G'olib tomon: {winner_name}",
        "",
    ]

    if winners:
        lines.append("👑 G'oliblar:")

        for winner in winners:
            lines.append(
                f"• {player_name(winner)}"
            )

        lines.append("")

    if reason:
        lines.extend(
            [
                "📜 Sabab:",
                reason,
                "",
            ]
        )

    lines.extend(
        [
            "🏰 Qirollikdagi jang yakunlandi.",
            "⚔️ Yangi tarix yozildi.",
        ]
    )

    return "\n".join(lines)


# ============================================================
# ROLE LIST
# ============================================================

def role_list_message(
    roles: List[Any],
) -> str:

    lines = [
        "🎭 THRONE — ROLLAR",
        "",
    ]

    for index, role in enumerate(roles, start=1):

        if isinstance(role, dict):
            name = role.get("name", "Noma'lum")
            side = role.get("side", "Noma'lum")
        else:
            name = getattr(role, "name", "Noma'lum")
            side = getattr(role, "side", "Noma'lum")

        lines.append(
            f"{index}. {name} — {side}"
        )

    return "\n".join(lines)


# ============================================================
# RULES
# ============================================================

def game_rules_message() -> str:

    return (
        "📖 THRONE — O'YIN QOIDALARI\n\n"
        "1️⃣ O'yinni faqat guruh administratori boshlaydi.\n"
        "2️⃣ Minimal o'yinchi soni — 7.\n"
        "3️⃣ Maksimal o'yinchi soni — 35.\n"
        "4️⃣ Har bir o'yinchiga yashirin rol beriladi.\n"
        "5️⃣ Tun vaqtida rollar yashirin harakat qiladi.\n"
        "6️⃣ Kunduzi o'yinchilar muhokama qiladi.\n"
        "7️⃣ Ovoz berish orqali o'yinchi chiqarilishi mumkin.\n"
        "8️⃣ Chiqarilgan o'yinchiga so'nggi so'z beriladi.\n"
        "9️⃣ G'alaba sharti tomon va maxsus rollarga bog'liq.\n"
        "🔟 Yashirin ma'lumotlarni boshqa o'yinchilarga "
        "ataylab oshkor qilish o'yin qoidalariga zid."
    )


# ============================================================
# GAME HELP
# ============================================================

def game_help_message() -> str:

    return (
        "❓ THRONE — O'YIN YORDAMI\n\n"
        "/newgame — yangi o'yin\n"
        "/join — o'yinga qo'shilish\n"
        "/start — o'yinni boshlash\n"
        "/leave — o'yinni tark etish\n"
        "/stop — o'yinni to'xtatish\n"
        "/rules — qoidalar\n"
        "/help — yordam\n\n"
        "👑 THRONE'da har bir qaror muhim."
    )


# ============================================================
# GAME PHASE
# ============================================================

def phase_message(
    phase: str,
) -> str:

    phases = {
        "lobby": "👥 O'yinchilar yig'ilmoqda.",
        "role_reveal": "🎭 Rollar taqsimlanmoqda.",
        "night": "🌙 Tun boshlandi.",
        "day": "🌅 Tong otdi.",
        "discussion": "💬 Muhokama boshlandi.",
        "voting": "⚖️ Ovoz berish boshlandi.",
        "last_words": "🕯️ So'nggi so'z vaqti.",
        "finished": "👑 O'yin yakunlandi.",
        "stopped": "🛑 O'yin to'xtatildi.",
    }

    return phases.get(
        phase,
        "🏰 THRONE davom etmoqda.",
    )


# ============================================================
# SPECTATOR MESSAGE
# ============================================================

def spectator_message() -> str:

    return (
        "👁️ TOMOSHABIN REJIMI\n\n"
        "☠️ Siz tirik o'yinchilar qatorida emassiz.\n\n"
        "📜 O'yinni kuzatishingiz mumkin,\n"
        "ammo yashirin harakatlarda qatnasha olmaysiz."
    )


# ============================================================
# ADMIN MESSAGE
# ============================================================

def admin_game_control_message() -> str:

    return (
        "⚙️ THRONE — ADMIN BOSHQARUVI\n\n"
        "👥 O'yinchilarni boshqarish\n"
        "▶️ O'yinni boshlash\n"
        "⏹️ O'yinni to'xtatish\n"
        "📊 O'yin holatini ko'rish\n"
        "🛡️ Xavfsizlik nazorati"
    )


# ============================================================
# ERROR MESSAGES
# ============================================================

def no_game_message() -> str:

    return (
        "⚠️ Hozir faol THRONE o'yini mavjud emas."
    )


def game_already_running_message() -> str:

    return (
        "⚠️ Hozir guruhda faol THRONE o'yini mavjud."
    )


def not_enough_players_message(
    minimum: int = 7,
) -> str:

    return (
        "⚠️ O'YINNI BOSHLAB BO'LMAYDI\n\n"
        f"👥 Kamida {minimum} nafar o'yinchi kerak."
    )


def not_admin_message() -> str:

    return (
        "⛔ Bu amalni faqat guruh administratori bajarishi mumkin."
    )


def not_player_message() -> str:

    return (
        "⚠️ Siz ushbu o'yin ishtirokchisi emassiz."
    )


# ============================================================
# FULL GAME STATUS
# ============================================================

def game_status_message(
    phase: str,
    round_number: int,
    alive_count: int,
    total_count: int,
) -> str:

    return (
        "👑 THRONE — O'YIN HOLATI\n\n"
        f"📍 Bosqich: {phase}\n"
        f"🔄 Raund: {round_number}\n"
        f"❤️ Tiriklar: {alive_count}/{total_count}\n\n"
        f"{phase_message(phase)}"
        )
