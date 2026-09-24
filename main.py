import os
import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CREATOR_ID = int(os.getenv("CREATOR_ID", "0"))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id == CREATOR_ID:
        text = (
            "👑 THRONE\n\n"
            "𓆩 ELITE 𓆪 YARATUVCHI\n\n"
            "🟡 Oltin: ∞\n"
            "🪙 Coin: ∞\n"
            "💎 Olmos: ∞\n"
            "⚜️ Elite Pass: AKTIV ∞\n\n"
            "🏰 The Kingdom Awaits."
        )
    else:
        text = (
            "👑 THRONE\n\n"
            "🏰 Qirollik seni kutmoqda.\n\n"
            "⚔️ Taxt uchun kurash boshlanadi.\n"
            "👑 O‘z qirolligingni qur."
        )

    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 THRONE — Yordam\n\n"
        "/start — O‘yinni boshlash\n"
        "/help — Yordam"
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("👑 THRONE bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
