from __future__ import annotations

from game_state import GamePhase, GameState, PlayerState
from roles import Side, get_role


class GameMessages:
    """THRONE o'yini uchun barcha guruh va shaxsiy xabarlar."""

    @staticmethod
    def game_created(game: GameState) -> str:
        return (
            "👑 <b>THRONE — Taxtlar O‘yini</b>\n\n"
            "Qirollik o‘yin uchun tayyor.\n"
            "⚔️ O‘yinchilar qo‘shilishini kutmoqda.\n\n"
            f"👥 O‘yinchilar: <b>{game.player_count()}</b>\n"
            f"🎯 Kerakli minimum: <b>4</b>\n\n"
            "👇 Quyidagi tugma orqali o‘yinga qo‘shiling."
        )

    @staticmethod
    def player_joined(
        player: PlayerState,
        game: GameState,
    ) -> str:
        return (
            f"⚔️ <b>{player.name}</b> o‘yinga qo‘shildi.\n\n"
            f"👥 O‘yinchilar: <b>{game.player_count()}</b>"
        )

    @staticmethod
    def player_left(
        player: PlayerState,
        game: GameState,
    ) -> str:
        return (
            f"🚪 <b>{player.name}</b> o‘yindan chiqdi.\n\n"
            f"👥 O‘yinchilar: <b>{game.player_count()}</b>"
        )

    @staticmethod
    def starting(game: GameState) -> str:
        return (
            "⏳ <b>THRONE</b>\n\n"
            "👑 Qirollik o‘yinni boshlashga tayyorlanmoqda...\n\n"
            f"👥 O‘yinchilar: <b>{game.player_count()}</b>\n"
            f"⏱ Boshlanish: <b>{game.start_time} soniya</b>"
        )

    @staticmethod
    def started(game: GameState) -> str:
        return (
            "👑 <b>THRONE — O‘YIN BOSHLANDI</b>\n\n"
            "⚔️ Har bir o‘yinchiga yashirin rol berildi.\n"
            "🌙 Birinchi tun boshlandi.\n\n"
            "📩 Rolingiz va shaxsiy vazifalaringiz bot orqali yuboriladi."
        )

    @staticmethod
    def night_started(game: GameState) -> str:
        return (
            f"🌙 <b>{game.day_number}-tun</b>\n\n"
            "Qirollik tun bag‘riga kirdi.\n"
            "🕯️ Har bir rol o‘zining tungi harakatini amalga oshirishi mumkin.\n\n"
            f"⏱ Vaqt: <b>{game.night_time} soniya</b>"
        )

    @staticmethod
    def day_started(game: GameState) -> str:
        return (
            f"☀️ <b>{game.day_number}-kun</b>\n\n"
            "⚔️ Endi muhokama vaqti.\n"
            "Har bir o‘yinchi o‘z fikrini bildirsin va shubhali harakatlarni muhokama qilsin.\n\n"
            f"⏱ Muhokama vaqti: <b>{game.day_time} soniya</b>\n\n"
            "🔔 Muhokama tugagach, ovoz berish shaxsiy chat orqali boshlanadi."
        )

    @staticmethod
    def voting_started(game: GameState) -> str:
        return (
            "🗳️ <b>OVOZ BERISH BOSHLANDI</b>\n\n"
            "Har bir tirik o‘yinchi faqat <b>1 ta ovoz</b> bera oladi.\n\n"
            "⚖️ Barcha ovozlar teng hisoblanadi.\n"
            "🚫 Durang bo‘lsa, hech kim chiqarilmaydi.\n"
            "🚫 Ovoz bermaslik ham mumkin.\n\n"
            f"⏱ Ovoz berish vaqti: <b>{game.vote_time} soniya</b>\n\n"
            "📩 Ovoz berish tugmalari shaxsiy chatga yuboriladi."
        )

    @staticmethod
    def voting_finished() -> str:
        return (
            "🗳️ <b>OVOZ BERISH YAKUNLANDI</b>\n\n"
            "Natijalar hisoblanmoqda..."
        )

    @staticmethod
    def no_elimination() -> str:
        return (
            "⚖️ <b>Hech kim chiqarilmadi.</b>\n\n"
            "Ovozlar teng bo‘ldi yoki yetarli ovoz berilmadi."
        )

    @staticmethod
    def player_eliminated(
        player: PlayerState,
        votes: int,
    ) -> str:
        role = get_role(player.role) if player.role else None
        role_name = role.name if role else "Noma’lum rol"

        return (
            "⚔️ <b>Ovoz berish natijasi</b>\n\n"
            f"☠️ <b>{player.name}</b> qirollikdan chiqarildi.\n"
            f"🗳️ Ovozlar: <b>{votes}</b>\n"
            f"🎭 Roli: <b>{role_name}</b>"
        )

    @staticmethod
    def players_list(game: GameState) -> str:
        lines = ["👥 <b>O‘yinchilar</b>\n"]

        for index, player in enumerate(
            game.players.values(),
            start=1,
        ):
            if not player.joined:
                status = "🚪 Chiqdi"
            elif player.alive:
                status = "🟢 Tirik"
            else:
                status = "☠️ Halok bo‘lgan"

            lines.append(
                f"{index}. {player.name} — {status}"
            )

        return "\n".join(lines)

    @staticmethod
    def death_message(
        player: PlayerState,
        cause: str = "night",
    ) -> str:
        role_key = player.role or ""
        name = player.name

        messages = {
            "shoh": (
                f"👑 {name} vafot etdi.\n"
                "Qirollik taxti endi vorisga muhtoj."
            ),
            "malika": (
                f"👸 {name} vafot etdi.\n"
                "Saroyning himoya devori qulab tushdi."
            ),
            "shahzoda": (
                f"🤴 {name} vafot etdi.\n"
                "Taxt vorisi endi yo‘q."
            ),
            "vazir": (
                f"🏛️ {name} vafot etdi.\n"
                "Qirollikning muhim sirlaridan biri yo‘qoldi."
            ),
            "bosh_qomondon": (
                f"⚔️ {name} vafot etdi.\n"
                "Qirollik qo‘shini bosh qo‘mondonidan ayrildi."
            ),
            "qirol_qoriqchisi": (
                f"🛡️ {name} vafot etdi.\n"
                "Taxtning sodiq qo‘riqchisi halok bo‘ldi."
            ),
            "qazi": (
                f"⚖️ {name} vafot etdi.\n"
                "Qirollik sudining ovozi jim bo‘ldi."
            ),
            "xazinachi": (
                f"💰 {name} vafot etdi.\n"
                "Qirollik xazinasi himoyachisini yo‘qotdi."
            ),
            "qishloq_aholisi": (
                f"🏘️ {name} vafot etdi.\n"
                "Oddiy xalq yana bir vakilidan ayrildi."
            ),
            "xizmatkor": (
                f"🧹 {name} vafot etdi.\n"
                "Saroydagi xizmatkor o‘z sirlarini olib ketdi."
            ),
            "ritsir": (
                f"🏰⚔️ {name} vafot etdi.\n"
                "Temir zirhli ritsir so‘nggi jangini o‘tkazdi."
            ),
            "aygoqchi": (
                f"🕵️ {name} vafot etdi.\n"
                "Qirollikning kuzatuvchisi endi hech kimni tekshira olmaydi."
            ),
            "soya_boshligi": (
                f"🕶️ {name} vafot etdi.\n"
                "Soya tomonining boshqaruvi zarbaga uchradi."
            ),
            "qotil": (
                f"🗡️ {name} vafot etdi.\n"
                "Soya qotili endi nishon ola olmaydi."
            ),
            "josus": (
                f"🕵️ {name} endi hech kimni kuzata olmaydi."
            ),
            "soxta_maslahatchi": (
                f"🎭 {name} vafot etdi.\n"
                "Yolg‘on maslahatlar manbai yo‘q qilindi."
            ),
            "xoin": (
                f"🩸 {name} vafot etdi.\n"
                "Xoinning siri oshkor bo‘ldi."
            ),
            "qora_vazir": (
                f"🖤 {name} vafot etdi.\n"
                "Qora saroyning vaziri yo‘q."
            ),
            "dushman_qiroli": (
                f"👑 {name} vafot etdi.\n"
                "Dushman taxtining egasi qulatildi."
            ),
            "dushman_qomondoni": (
                f"⚔️ {name} vafot etdi.\n"
                "Dushman qo‘shini qo‘mondonidan ayrildi."
            ),
            "dushman_josusi": (
                f"🕵️ {name} vafot etdi.\n"
                "Dushman josusining ma’lumotlari endi jim."
            ),
            "dushman_suiqasddchisi": (
                f"🗡️ {name} vafot etdi.\n"
                "Yashirin suiqasdchi yo‘q qilindi."
            ),
            "ovchi": (
                f"🐺 {name} vafot etdi.\n"
                "Ovchi o‘zining so‘nggi izini qoldirdi."
            ),
            "telba": (
                f"🃏 {name} vafot etdi.\n"
                "Telbaning taqdiri nihoyat yakunlandi."
            ),
            "sayyoh": (
                f"👤 {name} vafot etdi.\n"
                "Sayyohning uzoq safari shu yerda tugadi."
            ),
            "yollanma_jangchi": (
                f"⚔️ {name} vafot etdi.\n"
                "Yollanma jangchi shartnomasini bajara olmadi."
            ),
            "surgun_shahzoda": (
                f"🤴 {name} vafot etdi.\n"
                "Surgundagi shahzodaning qaytish umidi so‘ndi."
            ),
            "taxt_da_vogari": (
                f"👑 {name} vafot etdi.\n"
                "Taxt uchun da’vo shu yerda tugadi."
            ),
            "qaroqi": (
                f"🥷 {name} vafot etdi.\n"
                "Qaroqchining yashirin yo‘li yopildi."
            ),
            "sehrgar": (
                f"🧙 {name} vafot etdi.\n"
                "Sehr kuchi so‘ndi."
            ),
            "tabib": (
                f"🩺 {name} vafot etdi.\n"
                "Qirollik tabibi endi hech kimni davolay olmaydi."
            ),
            "kuzatuvchi": (
                f"👁️ {name} vafot etdi.\n"
                "Kuzatuvchining ko‘zlari yumildi."
            ),
            "qorovul": (
                f"🔒 {name} vafot etdi.\n"
                "Tun yo‘llarini to‘suvchi qorovul yo‘q."
            ),
            "solnomachi": (
                f"📜 {name} vafot etdi.\n"
                "Tarixni yozib boruvchi solnomachi jim bo‘ldi."
            ),
            "savdogar": (
                f"💰 {name} vafot etdi.\n"
                "Bozorning savdogari yo‘q."
            ),
            "suiqasddchi": (
                f"🗡️ {name} vafot etdi.\n"
                "Yashirin pichoq egasi halok bo‘ldi."
            ),
        }

        message = messages.get(
            role_key,
            f"☠️ {name} vafot etdi.",
        )

        if cause == "vote":
            return (
                f"{message}\n\n"
                "🗳️ Sabab: kunduzgi ovoz berish."
            )

        return (
            f"{message}\n\n"
            "🌙 Sabab: tungi voqea."
        )

    @staticmethod
    def survived_attack(
        player: PlayerState,
        reason: str,
    ) -> str:
        return (
            f"🛡️ <b>{player.name}</b> tungi hujumdan omon qoldi.\n"
            f"🔰 Sabab: {reason}"
        )

    @staticmethod
    def special_event(message: str) -> str:
        return f"✨ <b>Maxsus voqea</b>\n\n{message}"

    @staticmethod
    def inactivity_warning(
        player: PlayerState,
        nights_left: int,
    ) -> str:
        return (
            f"⚠️ <b>{player.name}</b>, siz ketma-ket faol bo‘lmadingiz.\n\n"
            f"🌙 Qolgan muddat: <b>{nights_left} tun</b>\n"
            "Agar faol bo‘lmasangiz, o‘yin sizni avtomatik chiqarishi mumkin."
        )

    @staticmethod
    def inactivity_removed(player: PlayerState) -> str:
        return (
            f"🚪 <b>{player.name}</b> uzoq vaqt faol bo‘lmagani "
            "sababli o‘yindan chiqarildi."
        )

    @staticmethod
    def final_words(player: PlayerState) -> str:
        return (
            f"📜 <b>{player.name}ning so‘nggi so‘zlari</b>\n\n"
            "«O‘yin davom etadi...»"
        )

    @staticmethod
    def automatic_final_words(player: PlayerState) -> str:
        return (
            f"📜 <b>{player.name}ning so‘nggi so‘zlari</b>\n\n"
            "«Men o‘z vazifamni bajardim. Qolgan taqdir sizniki...»"
        )

    @staticmethod
    def victory(
        winner: str,
        message: str | None = None,
    ) -> str:
        if message:
            return (
                "🏆 <b>THRONE — O‘YIN YAKUNLANDI</b>\n\n"
                f"👑 G‘olib: <b>{winner}</b>\n\n"
                f"{message}"
            )

        return (
            "🏆 <b>THRONE — O‘YIN YAKUNLANDI</b>\n\n"
            f"👑 G‘olib: <b>{winner}</b>\n\n"
            "⚔️ Qirollikdagi barcha voqealar o‘z yakuniga yetdi."
        )

    @staticmethod
    def role_card(player: PlayerState) -> str:
        if not player.role:
            return (
                "🎭 <b>Sizga rol berilmadi.</b>"
            )

        role = get_role(player.role)

        if role is None:
            return (
                "🎭 <b>Rol</b>\n\n"
                "Rol ma’lumoti topilmadi."
            )

        return (
            "🎭 <b>SIZNING ROLINGIZ</b>\n\n"
            f"{role.name}\n\n"
            f"🏰 Tomon: <b>{role.side.value}</b>\n"
            f"⚔️ Qobiliyat: {role.ability}\n\n"
            f"🎯 G‘alaba sharti: {role.win_condition}"
        )

    @staticmethod
    def shadow_teammates(
        game: GameState,
        player: PlayerState,
    ) -> str:
        if player.side != Side.SHOADOW.value:
            return ""

        teammates = []

        for other in game.players.values():
            if (
                other.user_id != player.user_id
                and other.joined
                and other.side == Side.SHOADOW.value
            ):
                role = get_role(other.role) if other.role else None
                role_name = role.name if role else "Noma’lum rol"

                teammates.append(
                    f"• {other.name} — {role_name}"
                )

        if not teammates:
            return (
                "🕶️ <b>SIZNING SHERIKLARINGIZ</b>\n\n"
                "Hozircha boshqa Soya o‘yinchisi yo‘q."
            )

        return (
            "🕶️ <b>SIZNING SHERIKLARINGIZ</b>\n\n"
            + "\n".join(teammates)
        )

    @staticmethod
    def phase_status(game: GameState) -> str:
        phase_names = {
            GamePhase.WAITING: "Kutish",
            GamePhase.STARTING: "Boshlanish",
            GamePhase.NIGHT: "Tun",
            GamePhase.DAY: "Kun",
            GamePhase.VOTING: "Ovoz berish",
            GamePhase.ENDED: "Yakunlangan",
        }

        phase_name = phase_names.get(
            game.phase,
            "Noma’lum",
        )

        return (
            "👑 <b>THRONE</b>\n\n"
            f"📍 Bosqich: <b>{phase_name}</b>\n"
            f"🌙 Kun/tun: <b>{game.day_number}</b>\n"
            f"👥 Tiriklar: <b>{game.alive_count()}</b>\n"
            f"🎮 Jami o‘yinchilar: <b>{game.player_count()}</b>"
        )

    @staticmethod
    def short_rules() -> str:
        return (
            "📖 <b>THRONE — Qisqa qoidalar</b>\n\n"
            "👑 O‘yin guruhda o‘tkaziladi.\n"
            "🎭 Har bir o‘yinchiga yashirin rol beriladi.\n"
            "🌙 Tunda rollar o‘z qobiliyatlaridan foydalanadi.\n"
            "☀️ Kunduzi o‘yinchilar muhokama qiladi.\n"
            "🗳️ Har bir tirik o‘yinchi 1 ta ovozga ega.\n"
            "⚖️ Barcha ovozlar teng hisoblanadi.\n"
            "🚫 Durangda hech kim chiqarilmaydi.\n"
            "☠️ Halok bo‘lgan o‘yinchilar ovoz bera olmaydi.\n"
            "🏆 G‘alaba tomon yoki shaxsiy vazifaga bog‘liq."
        )
