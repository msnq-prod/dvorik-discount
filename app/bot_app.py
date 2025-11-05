from __future__ import annotations

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.config import settings
from app.services.telegram_service import bot_auth, bot_main

redis_client = Redis.from_url(settings.REDIS_URL)
storage = RedisStorage(redis=redis_client)

dp_main = Dispatcher(storage=storage)
dp_auth = Dispatcher()

from app.routers import bot_auth as bot_auth_router  # noqa: E402  pylint: disable=wrong-import-position
from app.routers import bot_main as bot_main_router  # noqa: E402  pylint: disable=wrong-import-position

dp_main.include_router(bot_main_router.router)
dp_auth.include_router(bot_auth_router.router)

__all__ = ["dp_main", "dp_auth", "bot_main", "bot_auth"]
