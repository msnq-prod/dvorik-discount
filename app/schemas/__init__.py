from __future__ import annotations

from app.schemas.admins import AdminCreate, AdminSchema, AdminUpdate
from app.schemas.broadcasts import (
    BroadcastCreate,
    BroadcastLogSchema,
    BroadcastSchema,
    BroadcastUpdate,
)
from app.schemas.cashiers import CashierCreate, CashierSchema, CashierUpdate
from app.schemas.common import (
    CampaignCreate,
    CampaignSchema,
    CampaignUpdate,
    CampaignUserCreate,
    CampaignUserSchema,
    CampaignUserUpdate,
    SegmentCreate,
    SegmentSchema,
    SegmentUpdate,
    SettingCreate,
    SettingSchema,
    SettingUpdate,
)
from app.schemas.discount_templates import (
    DiscountTemplateCreate,
    DiscountTemplateSchema,
    DiscountTemplateUpdate,
)
from app.schemas.discount_usage_logs import (
    DiscountUsageLogCreate,
    DiscountUsageLogSchema,
)
from app.schemas.discounts import DiscountCreate, DiscountSchema, DiscountUpdate
from app.schemas.orders import AuditLogCreate, AuditLogSchema, OrderCreate, OrderSchema, OrderUpdate
from app.schemas.users import UserCreate, UserSchema, UserUpdate

__all__ = [
    "AdminCreate",
    "AdminSchema",
    "AdminUpdate",
    "AuditLogCreate",
    "AuditLogSchema",
    "BroadcastCreate",
    "BroadcastLogSchema",
    "BroadcastSchema",
    "BroadcastUpdate",
    "CampaignCreate",
    "CampaignSchema",
    "CampaignUpdate",
    "CampaignUserCreate",
    "CampaignUserSchema",
    "CampaignUserUpdate",
    "CashierCreate",
    "CashierSchema",
    "CashierUpdate",
    "DiscountCreate",
    "DiscountSchema",
    "DiscountTemplateCreate",
    "DiscountTemplateSchema",
    "DiscountTemplateUpdate",
    "DiscountUpdate",
    "DiscountUsageLogCreate",
    "DiscountUsageLogSchema",
    "OrderCreate",
    "OrderSchema",
    "OrderUpdate",
    "SegmentCreate",
    "SegmentSchema",
    "SegmentUpdate",
    "SettingCreate",
    "SettingSchema",
    "SettingUpdate",
    "UserCreate",
    "UserSchema",
    "UserUpdate",
]
