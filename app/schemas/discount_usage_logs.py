from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.discount_usage_logs import DiscountUsageStatus


class DiscountUsageLogBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    discount_id: int | None = None
    code: str
    cashier_id: int | None = None
    user_id: int | None = None
    status: DiscountUsageStatus
    message: str | None = None
    payload: dict[str, Any] | None = None


class DiscountUsageLogCreate(DiscountUsageLogBase):
    pass


class DiscountUsageLogSchema(DiscountUsageLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    class Config:
        from_attributes = True
