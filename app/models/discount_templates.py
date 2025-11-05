from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import DECIMAL, DateTime, Enum, Integer, JSON, String, Text, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.common import Campaign
    from app.models.discounts import Discount


class DiscountValueType(str, enum.Enum):
    percentage = "percentage"
    fixed = "fixed"


class DiscountEvent(str, enum.Enum):
    birthday = "birthday"
    subscription = "subscription"
    manual = "manual"


class DiscountUsageType(str, enum.Enum):
    single_use = "single_use"
    multi_use = "multi_use"


class DiscountTemplate(Base):
    __tablename__ = "discount_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    value: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    value_type: Mapped[DiscountValueType] = mapped_column(
        Enum(DiscountValueType, name="discount_value_type"), nullable=False
    )
    event: Mapped[DiscountEvent] = mapped_column(
        Enum(DiscountEvent, name="discount_event"), nullable=False
    )
    usage_type: Mapped[DiscountUsageType] = mapped_column(
        Enum(DiscountUsageType, name="discount_usage_type"), nullable=False
    )
    recurrence: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    is_active: Mapped[bool] = mapped_column(TINYINT(1), default=1, nullable=False)
    is_test: Mapped[bool] = mapped_column(TINYINT(1), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    discounts: Mapped[list["Discount"]] = relationship("Discount", back_populates="template")
    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="discount_template")
