from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.users import User


class BroadcastMediaType(str, enum.Enum):
    text = "text"
    photo = "photo"
    video = "video"


class BroadcastStatus(str, enum.Enum):
    draft = "draft"
    scheduled = "scheduled"
    sending = "sending"
    sent = "sent"
    error = "error"
    canceled = "canceled"


class BroadcastLogStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    skipped = "skipped"


class Broadcast(Base):
    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    media_type: Mapped[BroadcastMediaType] = mapped_column(
        Enum(BroadcastMediaType, name="broadcast_media_type"), nullable=False
    )
    media_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[BroadcastStatus] = mapped_column(
        Enum(BroadcastStatus, name="broadcast_status"), nullable=False, default=BroadcastStatus.draft
    )
    is_test: Mapped[bool] = mapped_column(TINYINT(1), default=0, nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    logs: Mapped[list["BroadcastLog"]] = relationship(
        "BroadcastLog", back_populates="broadcast", cascade="all, delete-orphan"
    )


class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    broadcast_id: Mapped[int] = mapped_column(
        ForeignKey("broadcasts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[BroadcastLogStatus] = mapped_column(
        Enum(BroadcastLogStatus, name="broadcast_log_status"), nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    broadcast: Mapped["Broadcast"] = relationship("Broadcast", back_populates="logs")
    user: Mapped["User | None"] = relationship("User", back_populates="broadcast_logs")
