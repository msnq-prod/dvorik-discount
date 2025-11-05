from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CashierBase(BaseModel):
    telegram_id: int
    username: str | None = None
    display_name: str | None = None
    is_active: bool = False
    approved_by_admin_id: int | None = None


class CashierCreate(CashierBase):
    pass


class CashierUpdate(BaseModel):
    username: str | None = None
    display_name: str | None = None
    is_active: bool | None = None
    approved_by_admin_id: int | None = None


class CashierSchema(CashierBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    class Config:
        from_attributes = True
