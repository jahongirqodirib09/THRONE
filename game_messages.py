from __future__ import annotations

from typing import Optional

from game_state import GamePhase, GameState, PlayerState
from roles import get_role


class GameMessages:
    """
    THRONE o'yinining barcha asosiy matnlarini boshqaradi.

    Bu fayl Telegram API bilan ishlamaydi.
    Faqat tayyor matnlarni qaytaradi.
    """

    # =========================================================
    # O'YIN BOSHLANISHI
    # =========================================================

    @staticmethod
    def game_created(game: GameState) -> str:
        return (
            "👑⚔️ THRONE — TAHTLAR O'YINI\n\n"
            "Qirollik uchun yangi o'yin ochildi.\n\n"
            f"👥 O'yinchilar: {game.player_count()}\n"
            f"🎯 Kerakli minimum: 4\n\n"
            "👇 O'yinga qo'shilish uchun tugmani bosing."
        )

    @staticmethod
    def player_joined(
        name: str,
        game: GameState,
    ) -> str:
        return (
            f"⚔️ {name} o'yinga qo'shildi.\n\n"
            f"👥 O'yinchilar: {game.player_count()}"
        )

    @staticmethod
    def player_left(
        name: str,
        game: GameState,
    ) -> str:
        return (
            f"🚪 {name} o'yindan chiqdi.\n\n"
            f"👥 O'yinchilar: {game.player_count()}"
        )

    @staticmethod
    def not_enough_players(
        current: int,
        minimum: int = 4,
    ) -> str:
        return (
            "⚠️ O'yinni boshlash uchun o'yinchilar yetarli emas.\n\n"
            f"👥 Hozir: {current}\n"
            f"🎯 Kerak: kamida {minimum}"
        )

    @staticmethod
    def starting(
        seconds: int,
        player_count: int,
    ) -> str:
        return (
            "👑⚔️ THRONE BOSHLANMOQDA\n\n"
            f"👥 O'yinchilar: {player_count}\n"
            f"⏳ Boshlanishiga: {seconds} soniya\n\n"
            "Rollar yashirin tarzda taqsimlanadi."
        )

    # =========================================================
    # O'YIN BOSHLANGAN
    # =========================================================

    @staticmethod
    def game_started(
        game: GameState,
    ) -> str:
        return (
            "👑⚔️ THRONE — TAHTLAR O'YINI\n\n"
            "Qirollik o'yini boshlandi.\n\n"
            f"👥 O'yinchilar: {game.player_count()}\n"
            f"🎭 Rollar: yashirin\n\n"
            "📩 Har bir o'yinchiga shaxsiy bot orqali "
            "uning roli yuboriladi.\n\n"
            "🌙 Birinchi tun boshlandi."
        )

    # =========================================================
    # TUN
    # =========================================================

    @staticmethod
    def night_started(
        game: GameState,
    ) -> str:
        return (
            f"🌙 {game.day_number}-TUN\n\n"
            "Qirollik sukunatga cho'mdi.\n"
            "Harakat qiladigan rollar o'z vazifalarini "
            "shaxsiy bot orqali bajaradi.\n\n"
            f"⏳ Tun: {game.night_time} soniya"
        )

    @staticmethod
    def night_ending(
        seconds: int,
    ) -> str:
        return (
            "🌙 Tun yakunlanmoqda...\n\n"
            f"⏳ {seconds} soniya qoldi."
        )

    @staticmethod
    def night_no_action(
        name: str,
    ) -> str:
        return (
            f"⚠️ {name} bu tun harakat qilmadi."
        )

    # =========================================================
    # KUN
    # =========================================================

    @staticmethod
    def day_started(
        game: GameState,
    ) -> str:
        return (
            f"☀️ {game.day_number}-KUN\n\n"
            "Tong otdi. Kechagi tun voqealari "
            "endi ma'lum bo'ladi.\n\n"
            f"🕐 Muhokama vaqti: {game.day_time} soniya\n\n"
            "🗣️ Muhokama qiling va shubhalaringizni ayting."
        )

    @staticmethod
    def day_discussion(
        game: GameState,
    ) -> str:
        return (
            f"☀️ {game.day_number}-kun.\n\n"
            "🗣️ Muhokama qiling.\n"
            f"⏳ {game.day_time} soniyadan so'ng "
            "ovoz berish boshlanadi."
        )

    # =========================================================
    # OVOZ BERISH
    # =========================================================

    @staticmethod
    def voting_started(
        game: GameState,
    ) -> str:
        return (
            "🗳️ OVOZ BERISH\n\n"
            "Kimni qirollikdan chiqarish kerak deb "
            "hisoblasangiz, tanlang.\n\n"
            f"⏳ Ovoz berish: {game.vote_time} soniya\n\n"
            "⚖️ Har bir tirik o'yinchi — 1 ta ovoz.\n"
            "🚫 Durang bo'lsa, hech kim chiqarilmaydi."
        )

    @staticmethod
    def private_voting(
        game: GameState,
    ) -> str:
        return (
            f"🗳️ {game.day_number}-KUN — OVOZ BERISH\n\n"
            "Kimni chiqarishni tanlang.\n\n"
            "⚖️ Har bir tirik o'yinchi faqat 1 ta "
            "ovozga ega.\n\n"
            "🚫 Ovoz bermaslik ham mumkin."
        )

    @staticmethod
    def vote_received() -> str:
        return (
            "✅ Ovozingiz qabul qilindi.\n\n"
            "Siz bu bosqichda qayta ovoz bera olmaysiz."
        )

    @staticmethod
    def vote_not_received() -> str:
        return (
            "⚠️ Ovoz qabul qilinmadi.\n"
            "Qaytadan tekshirib ko'ring."
        )

    @staticmethod
    def no_vote() -> str:
        return (
            "🚫 Siz bu safar ovoz bermadingiz."
        )

    @staticmethod
    def voting_tie() -> str:
        return (
            "⚖️ OVOZLAR TENG\n\n"
            "Hech bir o'yinchi chiqarilmadi.\n\n"
            "🌙 Keyingi tun boshlandi."
        )

    # =========================================================
    # O'YINCHI
    # =========================================================

    @staticmethod
    def player_card(
        player: PlayerState,
    ) -> str:
        role = get_role(player.role)

        role_name = (
            role.name
            if role is not None
            else "Noma'lum"
        )

        return (
            f"👤 {player.name}\n\n"
            f"🎭 Rol: {role_name}\n"
            f"❤️ Holat: "
            f"{'Tirik' if player.alive else 'Vafot etgan'}"
        )

    @staticmethod
    def alive_players(
        game: GameState,
    ) -> str:

        players = game.alive_players()

        lines = [
            "👥 TIRIK O'YINCHILAR",
            "",
        ]

        for index, player in enumerate(
            players,
            start=1,
        ):
            lines.append(
                f"{index}. {player.name}"
            )

        if not players:
            lines.append(
                "Tirik o'yinchi qolmagan."
            )

        return "\n".join(lines)

    # =========================================================
    # O'LIM
    # =========================================================

    @staticmethod
    def death_message(
        player: PlayerState,
        cause: str = "tun voqeasi",
    ) -> str:

        role = get_role(player.role)

        role_name = (
            role.name
            if role is not None
            else "Noma'lum rol"
        )

        role_key = player.role or ""

        special_messages = {
            "shoh": (
                f"👑 {player.name} qirollikdagi "
                "so'nggi jangidan qaytmadi."
            ),
            "malika": (
                f"👸 {player.name} saroyni "
                "himoya qila olmadi."
            ),
            "shahzoda": (
                f"🤴 {player.name}ning taxt sari yo'li "
                "shu yerda yakunlandi."
            ),
            "vazir": (
                f"🏛️ {player.name} saroy kengashidan ayrildi."
            ),
            "bosh_qomondon": (
                f"⚔️ {player.name} jang maydonida halok bo'ldi."
            ),
            "qirol_qoriqchisi": (
                f"🛡️ {player.name} so'nggi himoya chizig'ida yiqildi."
            ),
            "qazi": (
                f"⚖️ {player.name} hukm chiqaradigan emas, "
                "hukmga uchragan tomon bo'ldi."
            ),
            "xazinachi": (
                f"💰 {player.name} qirollik xazinasini "
                "endi himoya qila olmaydi."
            ),
            "qishloq_aholisi": (
                f"🏘️ {player.name} oddiy xalq orasidan "
                "yana bir qurbon bo'ldi."
            ),
            "xizmatkor": (
                f"🧹 {player.name} saroydagi xizmatini "
                "endi davom ettira olmaydi."
            ),
            "ritsir": (
                f"🏰⚔️ {player.name} zirhi ostida "
                "so'nggi jangini o'tkazdi."
            ),
            "aygoqchi": (
                f"🕵️ {player.name} bilgan sirlar "
                "o'zi bilan birga ketdi."
            ),
            "soya_boshligi": (
                f"🕶️ {player.name} soyalar ustidan "
                "hukmronligini yo'qotdi."
            ),
            "qotil": (
                f"🗡️ {player.name}ning o'zi ovga aylandi."
            ),
            "josus": (
                f"🕵️ {player.name endi hech kimni kuzata olmaydi."
            ),
            "soxta_maslahatchi": (
                f"🎭 {player.name}ning niqobi tushdi."
            ),
            "xoin": (
                f"🩸 {player.name}ning xiyonati "
                "oxir-oqibat o'ziga qaytdi."
            ),
            "qora_vazir": (
                f"🖤 {player.name}ning qora rejasi barbod bo'ldi."
            ),
            "dushman_qiroli": (
                f"👑 {player.name} dushman taxtini "
                "himoya qila olmadi."
            ),
            "dushman_qomondoni": (
                f"⚔️ {player.name} qo'shinini boshqara olmay qoldi."
            ),
            "dushman_josusi": (
                f"🕵️ {player.name}ning izlari shu yerda uzildi."
            ),
            "dushman_suiqasddchisi": (
                f"🗡️ {player.name} o'zining xavfli "
                "vazifasini yakunlay olmadi."
            ),
            "ovchi": (
                f"🐺 {player.name}ning ovi tugadi."
            ),
            "telba": (
                f"🃏 {player.name}ning taqdirini "
                "hech kim tushunib ulgurmay qoldi."
            ),
            "sayyoh": (
                f"👤 {player.name}ning uzoq safari "
                "shu yerda to'xtadi."
            ),
            "yollanma_jangchi": (
                f"⚔️ {player.name}ning navbatdagi "
                "shartnomasi bajarilmadi."
            ),
            "surgun_shahzoda": (
                f"🤴 {player.name}ning surgundagi yo'li yakunlandi."
            ),
            "taxt_davogari": (
                f"👑 {player.name} taxtga yetib bora olmadi."
            ),
            "qaroqi": (
                f"🥷 {player.name} o'g'irlangan boyliklari "
                "bilan birga yo'qoldi."
            ),
            "sehrgar": (
                f"🧙 {player.name}ning sehrlari bu safar yetarli bo'lmadi."
            ),
            "tabib": (
                f"🩺 {player.name} boshqalarni davoladi, "
                "ammo o'zini saqlab qola olmadi."
            ),
            "kuzatuvchi": (
                f"👁️ {player.name} kuzatgan so'nggi manzara shu bo'ldi."
            ),
            "qorovul": (
                f"🔒 {player.name}ning qorovulligi yakunlandi."
            ),
            "solnomachi": (
                f"📜 {player.name} yozib qoldirgan so'nggi sahifa yopildi."
            ),
            "savdogar": (
                f"💰 {player.name}ning bozordagi savdosi to'xtadi."
            ),
            "suiqasddchi": (
                f"🗡️ {player.name}ning yashirin missiyasi fosh bo'ldi."
            ),
        }

        text = special_messages.get(
            role_key,
            f"☠️ {player.name} o'yindan ayrildi.",
        )

        return (
            f"{text}\n\n"
            f"☠️ Roli: {role_name}\n"
            f"📜 Sabab: {cause}"
        )

    # =========================================================
    # ODDIY HIMOYA
    # =========================================================

    @staticmethod
    def survived_attack(
        player: PlayerState,
    ) -> str:

        role = get_role(player.role)

        role_name = (
            role.name
            if role is not None
            else "Noma'lum rol"
        )

        return (
            f"🛡️ {player.name} hujumdan omon qoldi.\n"
            f"🎭 Roli: {role_name}"
        )

    # =========================================================
    # MAXSUS HODISA
    # =========================================================

    @staticmethod
    def special_event(
        text: str,
    ) -> str:

        return (
            "📜 MUHIM VOQEA\n\n"
            f"{text}"
        )

    # =========================================================
    # FAOLIYAT
    # =========================================================

    @staticmethod
    def inactivity_warning(
        player: PlayerState,
        nights_left: int,
    ) -> str:

        return (
            f"⚠️ {player.name}, siz ketma-ket "
            f"faol bo'lmayapsiz.\n\n"
            f"🌙 Qolgan muddat: {nights_left} tun\n\n"
            "Faol bo'lmasangiz, o'yindan chiqarilishingiz mumkin."
        )

    @staticmethod
    def inactivity_removed(
        player: PlayerState,
    ) -> str:

        return (
            f"🚪 {player.name} faollik yetishmagani sababli "
            "o'yindan chiqarildi."
        )

    # =========================================================
    # SO'NGGI SO'Z
    # =========================================================

    @staticmethod
    def final_words(
        player: PlayerState,
        text: Optional[str],
    ) -> str:

        if text:
            return (
                f"🕯️ {player.name}ning so'nggi so'zi:\n\n"
                f"“{text}”"
            )

        return (
            f"🕯️ {player.name} so'nggi so'z qoldirmadi."
        )

    # =========================================================
    # G'ALABA
    # =========================================================

    @staticmethod
    def victory(
        winner: str,
    ) -> str:

        icons = {
            "TAHT": "👑",
            "SOYA": "🕶️",
            "YAKKA": "⚔️",
            "MAXSUS": "✨",
            "hech kim": "☠️",
        }

        icon = icons.get(
            winner,
            "🏆",
        )

        return (
            "🏆⚔️ THRONE — O'YIN YAKUNLANDI\n\n"
            f"{icon} G'olib tomon: {winner}\n\n"
            "Barcha natijalar qayd etildi."
        )

    # =========================================================
    # ROL OCHILISHI
    # =========================================================

    @staticmethod
    def role_reveal(
        player: PlayerState,
    ) -> str:

        role = get_role(player.role)

        if role is None:
            return (
                "🎭 Sizning rolingiz aniqlanmadi."
            )

        return (
            "🎭 SIZNING ROLINGIZ\n\n"
            f"{role.name}\n\n"
            f"⚔️ Tomon: {role.side.value}\n"
            f"✨ Qobiliyat: {role.ability}\n\n"
            f"🏆 G'alaba sharti:\n"
            f"{role.win_condition}"
        )

    # =========================================================
    # SOYA SHERIKLARI
    # =========================================================

    @staticmethod
    def shadow_teammates(
        game: GameState,
        player: PlayerState,
    ) -> str:

        if player.role is None:
            return ""

        player_role = get_role(player.role)

        if player_role is None:
            return ""

        if player_role.side != Side.SHADOW:
            return ""

        teammates = []

        for other in game.players.values():

            if other.user_id == player.user_id:
                continue

            if not other.joined:
                continue

            role = get_role(other.role)

            if role is None:
                continue

            if role.side != Side.SHADOW:
                continue

            teammates.append(
                f"• {other.name} — {role.name}"
            )

        if not teammates:
            teammates.append(
                "• Sizning hozircha sherigingiz yo'q."
            )

        return (
            "🕶️ SIZNING SHERIKLARINGIZ\n\n"
            "Soya tomoni o'yinchilari:\n"
            + "\n".join(teammates)
        )

    # =========================================================
    # FAZA
    # =========================================================

    @staticmethod
    def phase_status(
        game: GameState,
    ) -> str:

        phase_names = {
            GamePhase.WAITING: "⏳ Kutish",
            GamePhase.STARTING: "🚀 Boshlanish",
            GamePhase.NIGHT: "🌙 Tun",
            GamePhase.DAY: "☀️ Kun",
            GamePhase.VOTING: "🗳️ Ovoz berish",
            GamePhase.ENDED: "🏆 Yakunlangan",
        }

        phase_name = phase_names.get(
            game.phase,
            "Noma'lum",
        )

        return (
            "👑 THRONE\n\n"
            f"📍 Bosqich: {phase_name}\n"
            f"📅 Kun: {game.day_number}\n"
            f"👥 O'yinchilar: {game.player_count()}\n"
            f"❤️ Tiriklar: {game.alive_count()}"
        )

    # =========================================================
    # YORDAM
    # =========================================================

    @staticmethod
    def rules_short() -> str:

        return (
            "📖 THRONE — QISQA QOIDALAR\n\n"
            "👥 O'yin guruhda o'tkaziladi.\n"
            "👑 O'yinni guruh administratori boshlaydi.\n"
            "🎭 Har bir o'yinchiga yashirin rol beriladi.\n"
            "🌙 Tunda rollar o'z qobiliyatlaridan foydalanadi.\n"
            "☀️ Kunduzi o'yinchilar muhokama qiladi.\n"
            "🗳️ Ovoz berishda har bir tirik o'yinchi 1 ta "
            "ovozga ega.\n"
            "⚖️ Durang bo'lsa hech kim chiqarilmaydi.\n"
            "🏆 G'alaba sharti rol va tomoniga bog'liq."
  )
