from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.broadcasts import (
    BroadcastLogStatus,
    BroadcastMediaType,
    BroadcastStatus,
)


class BroadcastBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    title: str
    body: str
    media_type: BroadcastMediaType = BroadcastMediaType.text
    media_payload: dict[str, Any] | None = None
    status: BroadcastStatus = BroadcastStatus.draft
    is_test: bool = False
    scheduled_at: datetime | None = None


class BroadcastCreate(BroadcastBase):
    pass


class BroadcastUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    title: str | None = None
    body: str | None = None
    media_type: BroadcastMediaType | None = None
    media_payload: dict[str, Any] | None = None
    status: BroadcastStatus | None = None
    is_test: bool | None = None
    scheduled_at: datetime | None = None
    sent_at: datetime | None = None


class BroadcastSchema(BroadcastBase):
    id: int
    sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    class Config:
        from_attributes = True


class BroadcastLogBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    broadcast_id: int
    user_id: int | None = None
    status: BroadcastLogStatus
    error_message: str | None = None
    error_payload: dict[str, Any] | None = None


class BroadcastLogSchema(BroadcastLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    class Config:
        from_attributes = True
