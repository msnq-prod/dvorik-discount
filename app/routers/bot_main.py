from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime, timezone
from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.models.common import Campaign  # noqa: F401
from app.models.discounts import Discount
from app.models.users import User
from app.services import DiscountService, SubscriptionService

router = Router()


class BirthdayInput(StatesGroup):
    waiting_for_date = State()


def _parse_birthday(text: str) -> date:
    normalized = text.replace("/", ".").strip()
    today = date.today()
    min_year = 1920
    max_year = today.year - 14

    possible_formats = [
        "%d.%m.%Y",  # D.M.Y
        "%Y.%m.%d",  # Y.M.D
        "%d.%m.%y",  # D.M.YY
        "%y.%m.%d",  # YY.M.D
    ]

    parsed_date: date | None = None
    for fmt in possible_formats:
        try:
            parsed_date = datetime.strptime(normalized, fmt).date()
            break
        except ValueError:
            continue

    if parsed_date is None:
        raise ValueError("Invalid birthday format")

    if parsed_date >= today:
        raise ValueError("Birthday cannot be in the future")

    if not (min_year <= parsed_date.year <= max_year):
        raise ValueError(f"Birthday year must be between {min_year} and {max_year}")

    return parsed_date


from app.db import SessionLocal


async def _get_session() -> SessionLocal:
    return SessionLocal()


async def _get_or_create_user(db: SessionLocal, message: Message) -> User:
    telegram_id = message.from_user.id if message.from_user else None
    if telegram_id is None:
        raise RuntimeError("Telegram user is not available")

    stmt = select(User).where(User.telegram_id == telegram_id)
    user = (await db.execute(stmt)).scalars().first()
    is_test = bool(getattr(message.bot, "token", "") == settings.TELEGRAM_MAIN_BOT_TOKEN)

    changed = False

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=message.from_user.username if message.from_user else None,
            first_name=message.from_user.first_name if message.from_user else None,
            last_name=message.from_user.last_name if message.from_user else None,
            display_name=message.from_user.full_name if message.from_user else None,
            tags={},
            is_test=is_test,
        )
        db.add(user)
        changed = True
    else:
        if user.username != (message.from_user.username if message.from_user else user.username):
            user.username = message.from_user.username if message.from_user else user.username
            changed = True
        if user.first_name != (message.from_user.first_name if message.from_user else user.first_name):
            user.first_name = message.from_user.first_name if message.from_user else user.first_name
            changed = True
        if user.last_name != (message.from_user.last_name if message.from_user else user.last_name):
            user.last_name = message.from_user.last_name if message.from_user else user.last_name
            changed = True
        if user.display_name != (message.from_user.full_name if message.from_user else user.display_name):
            user.display_name = message.from_user.full_name if message.from_user else user.display_name
            changed = True
        if user.is_test != is_test:
            user.is_test = is_test
            changed = True

    ref_code = None
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) == 2 and parts[1].startswith("ref_"):
            ref_code = parts[1]

    if ref_code:
        user.tags = user.tags or {}
        if user.tags.get("ref") != ref_code:
            user.tags["ref"] = ref_code
            changed = True

    if changed:
        await db.commit()
        await db.refresh(user)
    return user


@router.message(Command("start"))
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    db = await _get_session()
    try:
        user = await _get_or_create_user(db, message)
    finally:
        await db.close()

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Мои скидки"),
                KeyboardButton(text="Проверить подписку"),
                KeyboardButton(text="Указать ДР"),
            ]
        ],
        resize_keyboard=True,
    )

    try:
        await message.answer(
            "Привет! Добро пожаловать в Мармеладный дворик.",
            reply_markup=keyboard,
        )
    except TelegramAPIError:
        await message.answer("Не удалось выполнить операцию, попробуйте позже")


@router.message(F.text == "Указать ДР")
async def request_birthday(message: Message, state: FSMContext) -> None:
    await message.answer("Введите дату рождения (например, 03.02.2002)")
    await state.set_state(BirthdayInput.waiting_for_date)


@router.message(BirthdayInput.waiting_for_date, F.text)
async def set_birthday(message: Message, state: FSMContext) -> None:
    try:
        birthday_value = _parse_birthday(message.text or "")
    except ValueError:
        await message.answer("Неверный формат. Попробуйте ещё раз в формате ДД.ММ.ГГГГ")
        return

    db = await _get_session()
    try:
        user = await _get_or_create_user(db, message)
        user.birthday = birthday_value
        db.add(user)
        await db.commit()
    finally:
        await db.close()

    await state.clear()
    try:
        await message.answer("Дата рождения сохранена!")
    except TelegramAPIError:
        await message.answer("Не удалось выполнить операцию, попробуйте позже")


@router.message(Command("cancel"), state="*")
async def cancel_state(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменено")


@router.message(F.text == "Проверить подписку")
async def check_subscription(message: Message) -> None:
    db = await _get_session()
    try:
        user = await _get_or_create_user(db, message)
        sub_service = SubscriptionService()
        is_member = await sub_service.check_subscription(db, user, settings.TELEGRAM_CHANNEL_ID)

        if is_member:
            discount_service = DiscountService()
            discount = discount_service.give_discount_from_template(db, user, "subscription")
            if discount:
                try:
                    await message.answer(f"Ваша скидка: {discount.code}")
                except TelegramAPIError:
                    await message.answer("Не удалось выполнить операцию, попробуйте позже")
            else:
                try:
                    await message.answer("Вы уже получали скидку по этой подписке")
                except TelegramAPIError:
                    await message.answer("Не удалось выполнить операцию, попробуйте позже")
        else:
            try:
                await message.answer("Вы не подписаны на канал")
            except TelegramAPIError:
                await message.answer("Не удалось выполнить операцию, попробуйте позже")
    finally:
        await db.close()


@router.message(F.text == "Мои скидки")
async def list_discounts(message: Message) -> None:
    db = await _get_session()
    try:
        user = await _get_or_create_user(db, message)
        stmt = (
            select(Discount)
            .where(
                Discount.user_id == user.id,
                Discount.used_at.is_(None),
                (Discount.expires_at.is_(None)) | (Discount.expires_at > datetime.now(timezone.utc)),
            )
            .order_by(Discount.expires_at.asc())
        )
        discounts: Sequence[Discount] = (await db.execute(stmt)).scalars().all()

        if not discounts:
            try:
                await message.answer("У вас нет активных скидок")
            except TelegramAPIError:
                await message.answer("Не удалось выполнить операцию, попробуйте позже")
            return

        lines = []
        for discount in discounts:
            if discount.expires_at:
                expires = discount.expires_at.strftime("%d.%m.%Y")
                lines.append(f"Код {discount.code} действует до {expires}")
            else:
                lines.append(f"Код {discount.code} без срока действия")

        try:
            await message.answer("\n".join(lines))
        except TelegramAPIError:
            await message.answer("Не удалось выполнить операцию, попробуйте позже")
    finally:
        await db.close()
