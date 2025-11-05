from __future__ import annotations

import logging
import random
import string
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.discount_templates import DiscountEvent, DiscountTemplate
from app.models.discounts import Discount
from app.models.users import User

logger = logging.getLogger(__name__)

CYRILLIC_ALPHABET: str = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ"


def _generate_discount_code() -> str:
    letters = "".join(random.choice(CYRILLIC_ALPHABET) for _ in range(3))
    digits = "".join(random.choice(string.digits) for _ in range(4))
    return f"{letters}{digits}"


async def is_code_unique(db: Session, code: str) -> bool:
    stmt = select(Discount.id).where(Discount.code == code)
    return (await db.execute(stmt)).scalar_one_or_none() is None


async def create_unique_discount_code(db: Session) -> str:
    for _ in range(5):
        candidate = _generate_discount_code()
        if await is_code_unique(db, candidate):
            return candidate
    raise RuntimeError("Could not generate a unique discount code after 5 attempts")


class DiscountService:
    """Handle discount issuance logic based on templates."""

    async def give_discount_from_template(
        self, db: Session, user: User, template_event: str
    ) -> Discount | None:
        try:
            event_enum = DiscountEvent(template_event)
        except ValueError:
            logger.warning("Unknown discount event requested: %s", template_event)
            return None

        template_stmt = (
            select(DiscountTemplate)
            .where(DiscountTemplate.event == event_enum, DiscountTemplate.is_active == 1)
            .order_by(DiscountTemplate.created_at.desc())
        )
        template = (await db.execute(template_stmt)).scalars().first()
        if template is None:
            logger.info("No active template found for event %s", template_event)
            return None

        if not await self._can_issue_from_template(db, user, template):
            return None

        code = await create_unique_discount_code(db)
        duration_days = template.duration_days or 0
        expires_at = None
        if duration_days > 0:
            expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)

        new_discount = Discount(
            user_id=user.id,
            template_id=template.id,
            code=code,
            expires_at=expires_at,
            is_test=user.is_test,
        )
        db.add(new_discount)
        await db.commit()
        await db.refresh(new_discount)
        return new_discount

    async def _can_issue_from_template(
        self, db: Session, user: User, template: DiscountTemplate
    ) -> bool:
        recurrence = template.recurrence or {}
        if not recurrence:
            return True

        rule_type = recurrence.get("type")
        if rule_type not in {"days", "monthly"}:
            return True

        if rule_type == "monthly":
            interval_days = settings.MONTHLY_DISCOUNT_INTERVAL_DAYS
        else:
            try:
                interval_days = int(recurrence.get("value", 0))
            except (TypeError, ValueError):
                interval_days = 0

        if interval_days <= 0:
            return True

        stmt = (
            select(Discount)
            .where(Discount.user_id == user.id, Discount.template_id == template.id)
            .order_by(Discount.created_at.desc())
        )
        last_discount = (await db.execute(stmt)).scalars().first()
        if last_discount is None or last_discount.created_at is None:
            return True

        last_created = last_discount.created_at
        if last_created.tzinfo is None:
            last_created = last_created.replace(tzinfo=timezone.utc)

        cutoff = datetime.now(timezone.utc) - timedelta(days=interval_days)
        return last_created <= cutoff
