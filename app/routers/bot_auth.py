from __future__ import annotations

from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.admins import Admin, AdminRole
from app.models.cashiers import Cashier
from app.models.discount_usage_logs import DiscountUsageLog, DiscountUsageStatus
from app.models.discounts import Discount
from app.models.users import User
from app.services import TelegramService, bot_main

router = Router()


async def _get_session() -> SessionLocal:
    return SessionLocal()


async def _get_or_create_cashier(db: SessionLocal, message: Message) -> Cashier:
    telegram_id = message.from_user.id if message.from_user else None
    if telegram_id is None:
        raise RuntimeError("Telegram user is not available")

    stmt = select(Cashier).where(Cashier.telegram_id == telegram_id)
    cashier = (await db.execute(stmt)).scalars().first()
    if cashier:
        return cashier

    cashier = Cashier(
        telegram_id=telegram_id,
        username=message.from_user.username if message.from_user else None,
        display_name=message.from_user.full_name if message.from_user else None,
        is_active=False,
    )
    db.add(cashier)

    admin_stmt = select(Admin).where(Admin.telegram_id == telegram_id)
    admin = (await db.execute(admin_stmt)).scalars().first()
    if admin is None:
        admin = Admin(
            telegram_id=telegram_id,
            username=message.from_user.username if message.from_user else None,
            display_name=message.from_user.full_name if message.from_user else None,
            role=AdminRole.readonly,
            is_active=False,
        )
        db.add(admin)

    await db.commit()
    return cashier


def _normalize_code(text: str) -> str:
    code = (text or "").strip().upper()
    if code.startswith(settings.DISCOUNT_CODE_PREFIX):
        parts = code.split(maxsplit=1)
        code = parts[1] if len(parts) > 1 else code.replace(settings.DISCOUNT_CODE_PREFIX, "", 1)
    return code.strip()


async def _find_discount(db: SessionLocal, code: str, for_update: bool = False) -> Discount | None:
    stmt = select(Discount).where(Discount.code == code)
    if for_update:
        stmt = stmt.with_for_update()
    return (await db.execute(stmt)).scalars().first()


async def _validate_discount(db: SessionLocal, code: str, for_update: bool = False) -> tuple[Discount | None, str | None]:
    discount = await _find_discount(db, code, for_update=for_update)
    if discount is None:
        return None, "Код не найден"

    if discount.used_at is not None:
        return None, "Код уже погашен"

    if discount.expires_at and discount.expires_at <= datetime.now(timezone.utc):
        return None, "Код истёк"

    user = await db.get(User, discount.user_id)
    if user is None:
        return None, "Код недействителен"

    return discount, None


@router.message(F.text)
async def handle_cashier_message(message: Message) -> None:
    db = await _get_session()
    try:
        cashier = await _get_or_create_cashier(db, message)
        if not cashier.is_active:
            await message.answer("Ваш запрос на рассмотрении")
            return

        code = _normalize_code(message.text)
        if not code:
            await message.answer("Пожалуйста, отправьте код скидки")
            return

        discount, error_message = await _validate_discount(db, code)

        if error_message:
            log = DiscountUsageLog(
                cashier_id=cashier.id,
                code=code,
                status=DiscountUsageStatus.not_found if error_message == "Код не найден" else
                DiscountUsageStatus.already_used if error_message == "Код уже погашен" else
                DiscountUsageStatus.expired if error_message == "Код истёк" else
                DiscountUsageStatus.invalid,
                message=error_message,
            )
            db.add(log)
            await db.commit()
            await message.answer(error_message)
            return

        user = await db.get(User, discount.user_id)
        if user is None:
            log = DiscountUsageLog(
                cashier_id=cashier.id,
                discount_id=discount.id,
                code=code,
                status=DiscountUsageStatus.invalid,
            )
            db.add(log)
            await db.commit()
            await message.answer("Код недействителен")
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Погасить", callback_data=f"redeem:{code}")]]
        )
        customer_name = user.display_name or user.username or str(user.telegram_id)
        await message.answer(f"Код валиден. Клиент: {customer_name}. Погасить?", reply_markup=keyboard)
    finally:
        await db.close()


@router.callback_query(F.data.startswith("redeem:"))
async def redeem_code(callback: CallbackQuery) -> None:
    if callback.data is None or callback.from_user is None:
        await callback.answer("Невозможно обработать", show_alert=True)
        return

    code = callback.data.split(":", 1)[1]
    db = await _get_session()
    try:
        stmt_cashier = select(Cashier).where(Cashier.telegram_id == callback.from_user.id)
        cashier = (await db.execute(stmt_cashier)).scalars().first()
        if cashier is None or not cashier.is_active:
            await callback.answer("Недостаточно прав", show_alert=True)
            return

        discount, error_message = await _validate_discount(db, code, for_update=True)
        if error_message:
            await callback.answer(error_message, show_alert=True)
            return

        user = await db.get(User, discount.user_id)
        if user is None:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        discount.used_at = datetime.now(timezone.utc)
        log = DiscountUsageLog(
            discount_id=discount.id,
            cashier_id=cashier.id,
            user_id=user.id,
            code=code,
            status=DiscountUsageStatus.success,
        )
        db.add(log)
        await db.commit()

        await callback.answer("Погашено ✅", show_alert=True)
        if callback.message:
            await callback.message.edit_reply_markup()

        if user.telegram_id:
            await TelegramService.send_message(
                bot_main,
                chat_id=user.telegram_id,
                text=f"Ваш код {code} использован.",
            )
    finally:
        await db.close()
