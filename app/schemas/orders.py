from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.logs_and_orders import OrderStatus


class OrderBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    user_id: int | None = None
    external_id: str | None = None
    status: OrderStatus = OrderStatus.pending
    total_amount: Decimal | None = None
    currency: str | None = None
    items: dict[str, Any] | None = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    status: OrderStatus | None = None
    total_amount: Decimal | None = None
    currency: str | None = None
    items: dict[str, Any] | None = None


class OrderSchema(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    class Config:
        from_attributes = True


class AuditLogBase(BaseModel):
    admin_id: int | None = None
    action: str
    payload: dict[str, Any] | None = None
    description: str | None = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogSchema(AuditLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    class Config:
        from_attributes = True
