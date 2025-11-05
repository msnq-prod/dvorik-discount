from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models.discounts import Discount
from app.models.users import User
from app.services import TelegramService, bot_main


async def _send_reminder(discount_id: int) -> None:
    db = SessionLocal()
    try:
        discount = await db.get(Discount, discount_id)
        if discount is None:
            return
        if discount.used_at is not None:
            return
        if discount.expires_at is None or discount.expires_at <= datetime.now(timezone.utc):
            return

        stmt = select(User.telegram_id).where(User.id == discount.user_id)
        chat_id = (await db.execute(stmt)).scalar_one_or_none()
        if chat_id is None:
            return

        await TelegramService.send_message(
            bot_main,
            chat_id=int(chat_id),
            text=f"Ваша скидка {discount.code} скоро сгорит...",
        )
    finally:
        await db.close()


@celery_app.task(name="tasks.send_discount_reminder")
def send_discount_reminder(discount_id: int) -> None:
    asyncio.run(_send_reminder(discount_id))
