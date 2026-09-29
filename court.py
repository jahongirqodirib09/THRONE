from database import db, now, get_king, get_position_holder, set_position, clear_position, list_court

POSITIONS = ["Shoh", "Malika", "Vazir", "Shahzoda", "Bosh qo‘mondon", "Qirol qo‘riqchisi", "Qozi",
             "Xazinachi", "Tabib", "Josus", "Munajjim", "Saroy qo‘riqchisi", "Qushboqar", "Kotib",
             "Ovchi", "Yo‘lchi", "Jar soluvchi", "Ritsir"]

async def crown_king(user_id):
    await set_position("Shoh", user_id)
    return True

async def appoint(position, user_id):
    if position not in POSITIONS:
        return False
    await set_position(position, user_id)
    return True

async def dismiss(position):
    if position not in POSITIONS:
        return False
    await clear_position(position)
    return True

async def my_position(user_id):
    court = await list_court()
    for row in court:
        if row["user_id"] == user_id:
            return row["position"]
    return None

async def court_text():
    court = await list_court()
    if not court:
        return "👑 SARO — hozircha hech kim taxtga o‘tirmagan."
    lines = [f"• {row['position']}: {row['full_name']}" for row in court]
    return "👑 SARO A'ZOLARI\n\n" + "\n".join(lines)
