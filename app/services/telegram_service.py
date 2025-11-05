from __future__ import annotations

import logging
from typing import Any

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatMember, Message

from app.config import settings

logger = logging.getLogger(__name__)

bot_main: Bot = Bot(
    token=settings.TELEGRAM_MAIN_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)
bot_auth: Bot = Bot(
    token=settings.TELEGRAM_AUTH_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)


class TelegramService:
    """Wrapper around aiogram bot operations with simple error handling."""

    @staticmethod
    async def send_message(
        bot: Bot,
        chat_id: int,
        text: str,
        reply_markup: Any | None = None,
    ) -> Message | None:
        """Send a message and log Telegram API errors instead of bubbling them up."""

        try:
            return await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        except TelegramAPIError as exc:  # pragma: no cover - network interaction
            logger.warning(
                "Failed to send Telegram message",
                extra={"chat_id": chat_id, "text": text[:32] if text else ""},
                exc_info=exc,
            )
            return None

    @staticmethod
    async def get_chat_member(bot: Bot, chat_id: int | str, user_id: int) -> ChatMember:
        """Fetch chat member information for a user."""
        return await bot.get_chat_member(chat_id=chat_id, user_id=user_id)

    @staticmethod
    async def set_main_webhook() -> bool:
        """Configure webhook for the main bot."""

        try:
            await bot_main.set_webhook(url=settings.TELEGRAM_WEBHOOK_MAIN_URL)
            return True
        except TelegramAPIError as exc:  # pragma: no cover - network interaction
            logger.warning("Failed to set main webhook", exc_info=exc)
            return False

    @staticmethod
    async def set_auth_webhook() -> bool:
        """Configure webhook for the auth bot."""

        try:
            await bot_auth.set_webhook(url=settings.TELEGRAM_WEBHOOK_AUTH_URL)
            return True
        except TelegramAPIError as exc:  # pragma: no cover - network interaction
            logger.warning("Failed to set auth webhook", exc_info=exc)
            return False
