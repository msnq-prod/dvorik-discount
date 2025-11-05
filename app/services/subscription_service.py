from __future__ import annotations

import logging
from datetime import datetime, timezone

from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.users import User
from app.services.telegram_service import TelegramService, bot_main

logger = logging.getLogger(__name__)

redis_client: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)


class SubscriptionService:
    """Service that tracks Telegram channel membership with Redis caching."""

    def __init__(self, client: Redis | None = None) -> None:
        self._redis: Redis = client or redis_client

    async def check_subscription(self, db: Session, user: User, channel_id: str) -> bool:
        if user.telegram_id is None:
            logger.warning("User %s has no telegram_id, cannot verify subscription", user.id)
            return False

        cache_key = f"sub:{channel_id}:{user.id}"
        try:
            cached_status = await self._redis.get(cache_key)
        except RedisError as exc:  # pragma: no cover - network interaction
            logger.warning("Redis get failed for %s", cache_key, exc_info=exc)
            cached_status = None

        is_member: bool
        made_api_call = False
        if cached_status == "member":
            is_member = True
        elif cached_status == "not_member":
            is_member = False
        else:
            made_api_call = True
            # This call can now raise an exception, which is the desired behavior.
            member = await TelegramService.get_chat_member(bot_main, channel_id, user.telegram_id)
            is_member = bool(member and member.status in {"member", "administrator", "creator"})

        # Update user object and commit the transaction
        user.is_subscribed = is_member
        user.subscription_checked_at = datetime.now(timezone.utc)
        db.add(user)
        db.commit()

        # If we got the status from the API, update the cache.
        if made_api_call:
            ttl_value = "member" if is_member else "not_member"
            try:
                await self._redis.set(cache_key, ttl_value, ex=60)
            except RedisError as exc:  # pragma: no cover - network interaction
                logger.warning("Redis set failed for %s", cache_key, exc_info=exc)

        return is_member
