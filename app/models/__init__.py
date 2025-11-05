from __future__ import annotations

from app.models.admins import Admin, AdminRole
from app.models.broadcasts import (
    Broadcast,
    BroadcastLog,
    BroadcastLogStatus,
    BroadcastMediaType,
    BroadcastStatus,
)
from app.models.cashiers import Cashier
from app.models.common import (
    Campaign,
    CampaignStatus,
    CampaignUser,
    CampaignUserStatus,
    Segment,
    SegmentType,
    Setting,
)
from app.models.discount_templates import (
    DiscountEvent,
    DiscountTemplate,
    DiscountUsageType,
    DiscountValueType,
)
from app.models.discount_usage_logs import DiscountUsageLog, DiscountUsageStatus
from app.models.discounts import Discount
from app.models.logs_and_orders import AuditLog, Order, OrderStatus
from app.models.users import User, UserGender

__all__ = [
    "Admin",
    "AdminRole",
    "AuditLog",
    "Broadcast",
    "BroadcastLog",
    "BroadcastLogStatus",
    "BroadcastMediaType",
    "BroadcastStatus",
    "Campaign",
    "CampaignStatus",
    "CampaignUser",
    "CampaignUserStatus",
    "Cashier",
    "Discount",
    "DiscountEvent",
    "DiscountTemplate",
    "DiscountUsageLog",
    "DiscountUsageStatus",
    "DiscountUsageType",
    "DiscountValueType",
    "Order",
    "OrderStatus",
    "Segment",
    "SegmentType",
    "Setting",
    "User",
    "UserGender",
]
