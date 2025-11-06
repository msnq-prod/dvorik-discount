from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.base import BaseSchema
from app.schemas.enums import CampaignStatusEnum, CouponStatusEnum, DiscountTypeEnum


# CouponTemplate Schemas
class CouponTemplateBase(BaseSchema):
    name: str
    code_pattern: str
    discount_type: DiscountTypeEnum
    discount_value: float = Field(..., ge=0)
    min_purchase: Optional[float] = Field(None, ge=0)
    per_user_limit: Optional[int] = Field(None, ge=0)
    usage_limit: Optional[int] = Field(None, ge=0)
    expiration_days: Optional[int] = Field(None, ge=0)
    stacking_rules: dict = {}
    conditions: dict = {}


class CouponTemplateCreate(CouponTemplateBase):
    pass


class CouponTemplateUpdate(CouponTemplateBase):
    pass


class CouponTemplate(CouponTemplateBase):
    id: int


# Campaign Schemas
class CampaignBase(BaseSchema):
    name: str
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    channels: list = []
    ref_code: Optional[str] = None
    ref_url: Optional[str] = None
    template_id: Optional[int] = None
    status: CampaignStatusEnum = CampaignStatusEnum.draft
    utm: dict = {}
    attribution_window_days: int = Field(7, ge=1, le=90)


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(CampaignBase):
    pass


class Campaign(CampaignBase):
    id: int


# Coupon Schemas
class CouponBase(BaseSchema):
    code: str
    template_id: int
    client_id: Optional[int] = None
    campaign_id: Optional[int] = None
    status: CouponStatusEnum = CouponStatusEnum.draft
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    redeemed_at: Optional[datetime] = None
    redeemed_by_employee_id: Optional[int] = None
    redemption_amount: Optional[float] = Field(None, ge=0)
    fraud_flag: bool = False


class CouponCreate(CouponBase):
    pass


class CouponUpdate(CouponBase):
    pass


class Coupon(CouponBase):
    id: int


class CouponIssueRequest(BaseSchema):
    client_ref: str
    template_id: int
    campaign_id: Optional[int] = None
    expires_at: Optional[datetime] = None
