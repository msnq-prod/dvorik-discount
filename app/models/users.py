from __future__ import annotations

import enum
from datetime import datetime, date
from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, Date, DateTime, Enum, JSON, String, Text, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.broadcasts import BroadcastLog
    from app.models.discount_usage_logs import DiscountUsageLog
    from app.models.discounts import Discount
    from app.models.logs_and_orders import Order
    from app.models.common import CampaignUser


class UserGender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gender: Mapped[UserGender | None] = mapped_column(Enum(UserGender, name="user_gender"), nullable=True)
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_subscribed: Mapped[bool] = mapped_column(TINYINT(1), default=0, nullable=False)
    subscription_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tags: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_test: Mapped[bool] = mapped_column(TINYINT(1), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    discounts: Mapped[list["Discount"]] = relationship(
        "Discount", back_populates="user", cascade="all, delete-orphan"
    )
    discount_usage_logs: Mapped[list["DiscountUsageLog"]] = relationship(
        "DiscountUsageLog", back_populates="user"
    )
    campaign_memberships: Mapped[list["CampaignUser"]] = relationship(
        "CampaignUser", back_populates="user", cascade="all, delete-orphan"
    )
    broadcast_logs: Mapped[list["BroadcastLog"]] = relationship(
        "BroadcastLog", back_populates="user"
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
