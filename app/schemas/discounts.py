from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DiscountBase(BaseModel):
    user_id: int
    template_id: int | None = None
    code: str
    is_test: bool = False
    expires_at: datetime | None = None
    used_at: datetime | None = None


class DiscountCreate(DiscountBase):
    pass


class DiscountUpdate(BaseModel):
    template_id: int | None = None
    expires_at: datetime | None = None
    used_at: datetime | None = None


class DiscountSchema(DiscountBase):
    id: int
    issued_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    class Config:
        from_attributes = True
