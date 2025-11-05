from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.discount_templates import (
    DiscountEvent,
    DiscountUsageType,
    DiscountValueType,
)


class DiscountTemplateBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str
    description: str | None = None
    value: Decimal
    value_type: DiscountValueType
    event: DiscountEvent
    usage_type: DiscountUsageType
    recurrence: dict[str, Any] | None = None
    duration_days: int = 30
    is_active: bool = True
    is_test: bool = False


class DiscountTemplateCreate(DiscountTemplateBase):
    pass


class DiscountTemplateUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str | None = None
    description: str | None = None
    value: Decimal | None = None
    value_type: DiscountValueType | None = None
    event: DiscountEvent | None = None
    usage_type: DiscountUsageType | None = None
    recurrence: dict[str, Any] | None = None
    duration_days: int | None = None
    is_active: bool | None = None
    is_test: bool | None = None


class DiscountTemplateSchema(DiscountTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    class Config:
        from_attributes = True
