from aiogram.exceptions import TelegramBadRequest
from database import list_channels, claim_channel

async def publish(bot, channel_id, text):
    if channel_id:
        try:
            await bot.send_message(channel_id, text)
        except TelegramBadRequest:
            pass

async def is_subscribed(bot, user_id, channel_id):
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ("member", "administrator", "creator")
    except TelegramBadRequest:
        return False

async def check_required(bot, user_id):
    """Majburiy kanallardan biriga a'zo bo'lmagan bo'lsa, o'sha kanalni qaytaradi. Hammasiga a'zo bo'lsa None."""
    channels = await list_channels(required_only=True)
    for ch in channels:
        if not await is_subscribed(bot, user_id, ch["channel_id"]):
            return ch
    return None

async def claim_reward(user_id, channel_id):
    return await claim_channel(user_id, channel_id)

async def list_text():
    channels = await list_channels()
    if not channels:
        return "📢 Hozircha rasmiy kanallar yo‘q."
    lines = [f"• {ch['title'] or ch['username']} — {ch['reward_gold']} gold" for ch in channels]
    return "📢 THRONE KANALLARI\n\n" + "\n".join(lines)
