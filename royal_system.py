from dataclasses import dataclass
from typing import Dict, List, Optional


ROYAL_POSITIONS = {
    "king": {
        "name": "👑 Shoh",
        "power": 100,
        "description": "Qirollikning oliy hukmdori.",
        "permissions": [
            "kingdom_manage",
            "castle_manage",
            "army_manage",
            "treasury_manage",
            "royal_decree",
            "appoint_positions",
            "remove_positions",
            "declare_war",
        ],
    },
    "queen": {
        "name": "👸 Malika",
        "power": 85,
        "description": "Saroy va qirollik ittifoqlarining muhim vakili.",
        "permissions": [
            "court_manage",
            "alliance_manage",
            "family_manage",
            "royal_advice",
        ],
    },
    "vizier": {
        "name": "🏛️ Vazir",
        "power": 90,
        "description": "Shohning asosiy maslahatchisi. Mustaqil siyosiy qarorlar bera oladi.",
        "permissions": [
            "royal_advice",
            "court_manage",
            "economic_advice",
            "political_action",
        ],
    },
    "prince": {
        "name": "🤴 Shahzoda",
        "power": 75,
        "description": "Qirollik taxtining merosxo‘ri.",
        "permissions": [
            "royal_advice",
            "court_access",
            "succession_right",
        ],
    },
    "commander": {
        "name": "⚔️ Bosh qo‘mondon",
        "power": 80,
        "description": "Qirollik qo‘shinlarining bosh harbiy qo‘mondoni.",
        "permissions": [
            "army_manage",
            "army_training",
            "war_strategy",
            "defense_manage",
        ],
    },
    "royal_guard": {
        "name": "🛡️ Qirol qo‘riqchisi",
        "power": 65,
        "description": "Shoh va saroy xavfsizligini ta’minlaydi.",
        "permissions": [
            "protect_king",
            "castle_defense",
            "guard_manage",
        ],
    },
    "judge": {
        "name": "⚖️ Qozi",
        "power": 60,
        "description": "Qirollik sudlari va hukmlarini boshqaradi.",
        "permissions": [
            "court_judgment",
            "law_manage",
            "dispute_resolve",
        ],
    },
    "treasurer": {
        "name": "💰 Xazinachi",
        "power": 70,
        "description": "Qirollik xazinasi va iqtisodiy nazorat uchun javobgar.",
        "permissions": [
            "treasury_view",
            "treasury_manage",
            "economic_report",
        ],
    },
    "court_guard": {
        "name": "🗡️ Saroy qo‘riqchisi",
        "power": 55,
        "description": "Saroy ichki xavfsizligini himoya qiladi.",
        "permissions": [
            "court_defense",
            "castle_defense",
        ],
    },
    "secretary": {
        "name": "📜 Kotib",
        "power": 40,
        "description": "Qirollik hujjatlari va saroy yozuvlarini yuritadi.",
        "permissions": [
            "document_manage",
            "royal_records",
        ],
    },
    "royal_hunter": {
        "name": "🏹 Ovchi",
        "power": 50,
        "description": "Qirollik ovlari va maxsus topshiriqlarni bajaradi.",
        "permissions": [
            "hunt",
            "special_mission",
        ],
    },
    "messenger": {
        "name": "🔔 Jar soluvchi",
        "power": 35,
        "description": "Qirollik farmonlarini xalqqa yetkazadi.",
        "permissions": [
            "public_announcement",
            "royal_message",
        ],
    },
}


@dataclass
class RoyalResult:
    success: bool
    message: str = ""
    position: Optional[str] = None
    data: Optional[dict] = None


def get_position(position_id: str) -> Optional[dict]:
    return ROYAL_POSITIONS.get(position_id)


def get_all_positions() -> Dict[str, dict]:
    return {
        key: dict(value)
        for key, value in ROYAL_POSITIONS.items()
    }


def get_position_name(position_id: str) -> str:
    position = get_position(position_id)

    if not position:
        return "Noma’lum lavozim"

    return position["name"]


def get_position_power(position_id: str) -> int:
    position = get_position(position_id)

    if not position:
        return 0

    return int(position.get("power", 0))


def get_position_description(position_id: str) -> str:
    position = get_position(position_id)

    if not position:
        return "Lavozim topilmadi."

    return position["description"]


def get_position_permissions(
    position_id: str,
) -> List[str]:

    position = get_position(position_id)

    if not position:
        return []

    return list(
        position.get("permissions", [])
    )


def has_permission(
    position_id: str,
    permission: str,
) -> bool:

    return permission in get_position_permissions(
        position_id
    )


def get_positions_by_power(
    minimum_power: int = 0,
) -> List[dict]:

    result = []

    for position_id, position in ROYAL_POSITIONS.items():

        if position["power"] < minimum_power:
            continue

        result.append(
            {
                "id": position_id,
                **position,
            }
        )

    return sorted(
        result,
        key=lambda item: item["power"],
        reverse=True,
    )


def get_court_positions() -> List[dict]:
    return [
        {
            "id": position_id,
            **position,
        }
        for position_id, position
        in ROYAL_POSITIONS.items()
    ]


def validate_position(
    position_id: str,
) -> RoyalResult:

    if position_id not in ROYAL_POSITIONS:
        return RoyalResult(
            success=False,
            message="❌ Bunday qirollik lavozimi mavjud emas.",
        )

    position = get_position(position_id)

    return RoyalResult(
        success=True,
        position=position_id,
        message=f"✅ {position['name']} lavozimi mavjud.",
        data=position,
    )


def build_position_text(
    position_id: str,
) -> str:

    position = get_position(position_id)

    if not position:
        return "❌ Lavozim topilmadi."

    permissions = position.get(
        "permissions",
        [],
    )

    lines = [
        position["name"],
        "",
        f"⚔️ Siyosiy kuch: {position['power']}",
        "",
        f"📖 {position['description']}",
        "",
        "🔐 Huquqlar:",
    ]

    for permission in permissions:
        lines.append(
            f"• {permission}"
        )

    return "\n".join(lines)


def get_royal_positions_text() -> str:

    lines = [
        "👑 THRONE — SAROY LAVOZIMLARI",
        "",
    ]

    for position_id, position in ROYAL_POSITIONS.items():
        lines.append(
            f"{position['name']} — "
            f"{position['power']} kuch"
        )

    return "\n".join(lines)


def create_empty_court() -> dict:

    return {
        "king": None,
        "queen": None,
        "vizier": None,
        "prince": None,
        "commander": None,
        "royal_guard": None,
        "judge": None,
        "treasurer": None,
        "court_guard": None,
        "secretary": None,
        "royal_hunter": None,
        "messenger": None,
    }


def assign_position(
    court: dict,
    position_id: str,
    user_id: int,
) -> RoyalResult:

    if position_id not in ROYAL_POSITIONS:
        return RoyalResult(
            success=False,
            message="❌ Lavozim mavjud emas.",
        )

    if not user_id:
        return RoyalResult(
            success=False,
            message="❌ O‘yinchi aniqlanmadi.",
        )

    current = court.get(position_id)

    if current is not None:
        return RoyalResult(
            success=False,
            message=(
                f"❌ {get_position_name(position_id)} "
                "lavozimi allaqachon band."
            ),
        )

    court[position_id] = user_id

    return RoyalResult(
        success=True,
        position=position_id,
        message=(
            f"👑 {get_position_name(position_id)} "
            "lavozimiga tayinlandi."
        ),
        data={
            "user_id": user_id,
            "position": position_id,
        },
    )


def remove_position(
    court: dict,
    position_id: str,
) -> RoyalResult:

    if position_id not in ROYAL_POSITIONS:
        return RoyalResult(
            success=False,
            message="❌ Lavozim mavjud emas.",
        )

    if not court.get(position_id):
        return RoyalResult(
            success=False,
            message="❌ Bu lavozim bo‘sh.",
        )

    user_id = court[position_id]

    court[position_id] = None

    return RoyalResult(
        success=True,
        position=position_id,
        message=(
            f"🔓 {get_position_name(position_id)} "
            "lavozimi bo‘shatildi."
        ),
        data={
            "user_id": user_id,
        },
    )


def get_user_position(
    court: dict,
    user_id: int,
) -> Optional[str]:

    for position_id, assigned_user in court.items():

        if assigned_user == user_id:
            return position_id

    return None


def is_king(
    court: dict,
    user_id: int,
) -> bool:

    return court.get("king") == user_id


def is_queen(
    court: dict,
    user_id: int,
) -> bool:

    return court.get("queen") == user_id


def can_manage_court(
    court: dict,
    user_id: int,
) -> bool:

    position = get_user_position(
        court,
        user_id,
    )

    if not position:
        return False

    return has_permission(
        position,
        "appoint_positions",
    ) or position == "king"


def can_use_permission(
    court: dict,
    user_id: int,
    permission: str,
) -> bool:

    position = get_user_position(
        court,
        user_id,
    )

    if not position:
        return False

    return has_permission(
        position,
        permission,
    )


def calculate_court_power(
    court: dict,
) -> int:

    total = 0

    for position_id, user_id in court.items():

        if user_id:
            total += get_position_power(
                position_id
            )

    return total


def get_filled_positions(
    court: dict,
) -> List[dict]:

    result = []

    for position_id, user_id in court.items():

        if not user_id:
            continue

        result.append(
            {
                "position": position_id,
                "name": get_position_name(
                    position_id
                ),
                "user_id": user_id,
                "power": get_position_power(
                    position_id
                ),
            }
        )

    return result


def get_empty_positions(
    court: dict,
) -> List[str]:

    return [
        position_id
        for position_id in ROYAL_POSITIONS
        if not court.get(position_id)
    ]


def court_summary(
    court: dict,
) -> dict:

    filled = get_filled_positions(court)
    empty = get_empty_positions(court)

    return {
        "total_positions": len(
            ROYAL_POSITIONS
        ),
        "filled": len(filled),
        "empty": len(empty),
        "court_power": calculate_court_power(
            court
        ),
        "positions": filled,
    }


def court_dashboard(
    court: dict,
) -> str:

    summary = court_summary(court)

    lines = [
        "👑 QIROLLIK SAROYI",
        "",
        f"⚔️ Saroy kuchi: {summary['court_power']}",
        f"👥 Band lavozimlar: {summary['filled']}",
        f"🔓 Bo‘sh lavozimlar: {summary['empty']}",
        "",
    ]

    for position_id in ROYAL_POSITIONS:

        user_id = court.get(position_id)

        if user_id:
            lines.append(
                f"{get_position_name(position_id)} — "
                f"ID: {user_id}"
            )
        else:
            lines.append(
                f"{get_position_name(position_id)} — BO‘SH"
            )

    return "\n".join(lines)


def royal_decree(
    court: dict,
    user_id: int,
    decree: str,
) -> RoyalResult:

    if not is_king(court, user_id):
        return RoyalResult(
            success=False,
            message=(
                "❌ Faqat Shoh qirollik farmoni "
                "chiqara oladi."
            ),
        )

    if not decree or not decree.strip():
        return RoyalResult(
            success=False,
            message="❌ Farmon matni bo‘sh bo‘lishi mumkin emas.",
        )

    decree = decree.strip()

    if len(decree) > 500:
        return RoyalResult(
            success=False,
            message="❌ Farmon 500 belgidan oshmasligi kerak.",
        )

    return RoyalResult(
        success=True,
        message=(
            "📜 QIROLLIK FARMONI\n\n"
            f"👑 Shoh: {user_id}\n\n"
            f"📜 {decree}"
        ),
        data={
            "king_id": user_id,
            "decree": decree,
        },
    )


def oppose_king(
    court: dict,
    user_id: int,
    reason: str,
) -> RoyalResult:

    if not court.get("vizier") == user_id:
        return RoyalResult(
            success=False,
            message=(
                "❌ Bu siyosiy qarshilik huquqi "
                "Vazirga tegishli."
            ),
        )

    if not reason or not reason.strip():
        return RoyalResult(
            success=False,
            message="❌ Qarshilik sababi ko‘rsatilmagan.",
        )

    return RoyalResult(
        success=True,
        message=(
            "🏛️ VAZIRNING QARSHI QARORI\n\n"
            f"Vazir ID: {user_id}\n"
            f"📜 Sabab: {reason.strip()}"
        ),
        data={
            "user_id": user_id,
            "reason": reason.strip(),
            "opposed": True,
        },
    )


def royal_position_permissions(
    position_id: str,
) -> dict:

    position = get_position(position_id)

    if not position:
        return {}

    return {
        "position": position_id,
        "name": position["name"],
        "power": position["power"],
        "permissions": list(
            position.get(
                "permissions",
                [],
            )
        ),
    }


def serialize_court(
    court: dict,
) -> dict:

    return {
        "court": dict(court),
        "summary": court_summary(court),
    }


def royal_system_status() -> dict:

    return {
        "enabled": True,
        "positions": len(
            ROYAL_POSITIONS
        ),
        "court_management": True,
        "royal_decrees": True,
        "vizier_opposition": True,
        "permission_system": True,
    }


def royal_system_text() -> str:

    status = royal_system_status()

    return (
        "👑 THRONE ROYAL SYSTEM\n\n"
        f"Holat: {'AKTIV' if status['enabled'] else 'O‘CHIQ'}\n"
        f"Saroy lavozimlari: {status['positions']}\n"
        "🏛️ Saroy boshqaruvi: AKTIV\n"
        "📜 Qirollik farmonlari: AKTIV\n"
        "🏛️ Vazir qarshiligi: AKTIV\n"
        "🔐 Huquqlar tizimi: AKTIV"
)
