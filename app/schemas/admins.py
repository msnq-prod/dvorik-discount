from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.admins import AdminRole


class AdminBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    telegram_id: int
    username: str | None = None
    display_name: str | None = None
    role: AdminRole = AdminRole.readonly
    is_active: bool = False
    can_broadcast_from_chat: bool = False
    notification_groups: list[Any] | None = None


class AdminCreate(AdminBase):
    role: AdminRole = AdminRole.readonly


class AdminUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    role: AdminRole | None = None
    is_active: bool | None = None
    can_broadcast_from_chat: bool | None = None
    notification_groups: list[Any] | None = None


class AdminSchema(AdminBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    class Config:
        from_attributes = True
