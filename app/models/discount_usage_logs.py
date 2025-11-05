from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.cashiers import Cashier
    from app.models.discounts import Discount
    from app.models.users import User


class DiscountUsageStatus(str, enum.Enum):
    success = "success"
    already_used = "already_used"
    not_found = "not_found"
    expired = "expired"
    cashier_not_active = "cashier_not_active"
    invalid = "invalid"


class DiscountUsageLog(Base):
    __tablename__ = "discount_usage_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    discount_id: Mapped[int | None] = mapped_column(
        ForeignKey("discounts.id", ondelete="SET NULL"), nullable=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    cashier_id: Mapped[int | None] = mapped_column(
        ForeignKey("cashiers.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[DiscountUsageStatus] = mapped_column(
        Enum(DiscountUsageStatus, name="discount_usage_status"), nullable=False
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    discount: Mapped["Discount | None"] = relationship("Discount", back_populates="usage_logs")
    cashier: Mapped["Cashier | None"] = relationship("Cashier", back_populates="usage_logs")
    user: Mapped["User | None"] = relationship("User", back_populates="discount_usage_logs")
