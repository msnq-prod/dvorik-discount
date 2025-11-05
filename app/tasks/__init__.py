from __future__ import annotations

from app.tasks.birthday import send_birthday_congrats
from app.tasks.broadcasts import send_broadcast
from app.tasks.reminders import send_discount_reminder

__all__ = [
    "send_birthday_congrats",
    "send_broadcast",
    "send_discount_reminder",
]
