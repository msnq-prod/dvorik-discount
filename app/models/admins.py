from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, DateTime, Enum, JSON, String, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.cashiers import Cashier
    from app.models.logs_and_orders import AuditLog


class AdminRole(str, enum.Enum):
    owner = "owner"
    marketing = "marketing"
    readonly = "readonly"


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    role: Mapped[AdminRole] = mapped_column(Enum(AdminRole, name="admin_role"), nullable=False, default=AdminRole.readonly)
    is_active: Mapped[bool] = mapped_column(TINYINT(1), default=0, nullable=False)
    can_broadcast_from_chat: Mapped[bool] = mapped_column(TINYINT(1), default=0, nullable=False)
    notification_groups: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    approved_cashiers: Mapped[list["Cashier"]] = relationship(
        "Cashier", back_populates="approver"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="admin")
