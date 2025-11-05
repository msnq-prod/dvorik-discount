from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.users import UserGender


class UserBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    phone: str | None = None
    email: str | None = None
    gender: UserGender | None = None
    birthday: date | None = None
    tags: dict[str, Any] | None = None
    notes: str | None = None
    is_test: bool = False


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    phone: str | None = None
    email: str | None = None
    gender: UserGender | None = None
    birthday: date | None = None
    tags: dict[str, Any] | None = None
    notes: str | None = None
    is_test: bool | None = None
    is_subscribed: bool | None = None


class UserSchema(UserBase):
    id: int
    is_subscribed: bool
    subscription_checked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    class Config:
        from_attributes = True
