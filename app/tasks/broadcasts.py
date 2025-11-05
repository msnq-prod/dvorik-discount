from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter
from sqlalchemy import select

from app.celery_app import celery_app
from app.config import settings
from app.db import SessionLocal
from app.models.broadcasts import Broadcast, BroadcastLog, BroadcastLogStatus, BroadcastStatus
from app.models.users import User
from app.services import TelegramService, bot_main


@dataclass
class RetryLater(Exception):
    retry_after: int


async def _send_broadcast(broadcast_id: int) -> None:
    db = SessionLocal()
    broadcast: Broadcast | None = None
    try:
        broadcast = await db.get(Broadcast, broadcast_id)
        if broadcast is None:
            return

        broadcast.status = BroadcastStatus.sending
        db.add(broadcast)
        await db.commit()
        await db.refresh(broadcast)

        stmt = (
            select(User.id, User.telegram_id)
            .where(User.is_test == broadcast.is_test, User.telegram_id.is_not(None))
            .order_by(User.id)
        )
        recipients = (await db.execute(stmt)).all()

        delay = 60.0 / max(1, settings.DEFAULT_BROADCAST_RATE_PER_MINUTE)

        for user_id, chat_id in recipients:
            if chat_id is None:
                continue

            log: BroadcastLog | None = None
            try:
                await TelegramService.send_message(bot_main, chat_id=int(chat_id), text=broadcast.body)
                log = BroadcastLog(
                    broadcast_id=broadcast.id,
                    user_id=user_id,
                    status=BroadcastLogStatus.success,
                )
            except TelegramForbiddenError:
                log = BroadcastLog(
                    broadcast_id=broadcast.id,
                    user_id=user_id,
                    status=BroadcastLogStatus.failed,
                    error_message="blocked",
                )
            except TelegramRetryAfter as exc:
                raise RetryLater(int(exc.retry_after)) from exc
            except TelegramAPIError as exc:
                log = BroadcastLog(
                    broadcast_id=broadcast.id,
                    user_id=user_id,
                    status=BroadcastLogStatus.failed,
                    error_message=str(exc),
                )
            else:
                if delay > 0:
                    await asyncio.sleep(delay)
            finally:
                if log is not None:
                    db.add(log)
                    await db.commit()

        broadcast.status = BroadcastStatus.sent
        broadcast.sent_at = datetime.now(timezone.utc)
        db.add(broadcast)
        await db.commit()
    except RetryLater:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        if broadcast is not None:
            broadcast.status = BroadcastStatus.error
            db.add(broadcast)
            await db.commit()
        raise
    finally:
        await db.close()


@celery_app.task(name="tasks.send_broadcast", bind=True, max_retries=3)
def send_broadcast(self, broadcast_id: int) -> None:
    try:
        asyncio.run(_send_broadcast(broadcast_id))
    except RetryLater as exc:
        raise self.retry(countdown=exc.retry_after)


@celery_app.task(name="tasks.check_scheduled_broadcasts")
def check_scheduled_broadcasts() -> None:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Broadcast)
            .where(
                Broadcast.status == BroadcastStatus.scheduled,
                Broadcast.scheduled_at <= now,
            )
        )
        broadcasts = (await db.execute(stmt)).scalars().all()

        for broadcast in broadcasts:
            broadcast.status = BroadcastStatus.sending
            db.add(broadcast)
            await db.commit()
            send_broadcast.delay(broadcast.id)
    finally:
        await db.close()
