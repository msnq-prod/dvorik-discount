from __future__ import annotations

import asyncio
from datetime import datetime

import pytz
from sqlalchemy import select
from sqlalchemy import func

from app.celery_app import celery_app
from app.config import settings
from app.db import SessionLocal
from app.models.users import User
from app.services import DiscountService, TelegramService, bot_main


async def _run() -> None:
    db = SessionLocal()
    try:
        tz = pytz.timezone(settings.TZ)
        today = datetime.now(tz)
        stmt = (
            select(User)
            .where(
                User.birthday.is_not(None),
                func.day(User.birthday) == today.day,
                func.month(User.birthday) == today.month,
            )
        )
        users = (await db.execute(stmt)).scalars().all()
        if not users:
            return

        discount_service = DiscountService()
        for user in users:
            if user.telegram_id is None:
                continue
            await discount_service.give_discount_from_template(db, user, "birthday")
            await TelegramService.send_message(
                bot_main,
                chat_id=user.telegram_id,
                text="С Днем Рождения!",
            )
    finally:
        await db.close()


@celery_app.task(name="tasks.send_birthday_congrats")
def send_birthday_congrats() -> None:
    asyncio.run(_run())
