from database import db

LANGUAGES = {"uz": "O‘zbekcha", "ru": "Русский", "en": "English", "tr": "Türkçe", "ar": "العربية", "ky": "Кыргызча"}

async def set_language(user_id, code):
    if code not in LANGUAGES:
        return False
    async with db() as c:
        await c.execute("UPDATE users SET language=? WHERE user_id=?", (code, user_id))
    return True

async def get_language(user_id):
    async with db() as c:
        cur = await c.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
    return row["language"] if row and row["language"] else "uz"
