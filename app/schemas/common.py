from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.common import (
    CampaignStatus,
    CampaignUserStatus,
    SegmentType,
)


class SegmentBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str
    description: str | None = None
    type: SegmentType = SegmentType.dynamic
    definition: dict[str, Any] | None = None
    is_active: bool = True


class SegmentCreate(SegmentBase):
    pass


class SegmentUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str | None = None
    description: str | None = None
    type: SegmentType | None = None
    definition: dict[str, Any] | None = None
    is_active: bool | None = None


class SegmentSchema(SegmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    class Config:
        from_attributes = True


class CampaignBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str
    description: str | None = None
    segment_id: int | None = None
    discount_template_id: int | None = None
    status: CampaignStatus = CampaignStatus.draft
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    is_test: bool = False


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str | None = None
    description: str | None = None
    segment_id: int | None = None
    discount_template_id: int | None = None
    status: CampaignStatus | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    is_test: bool | None = None


class CampaignSchema(CampaignBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    class Config:
        from_attributes = True


class CampaignUserBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    campaign_id: int
    user_id: int
    status: CampaignUserStatus = CampaignUserStatus.pending


class CampaignUserCreate(CampaignUserBase):
    pass


class CampaignUserUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    status: CampaignUserStatus | None = None


class CampaignUserSchema(CampaignUserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    class Config:
        from_attributes = True


class SettingBase(BaseModel):
    key: str
    value: Any | None = None
    description: str | None = None


class SettingCreate(SettingBase):
    pass


class SettingUpdate(BaseModel):
    value: Any | None = None
    description: str | None = None


class SettingSchema(SettingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    class Config:
        from_attributes = True


class SettingsPatch(BaseModel):
    APP_ENV: str | None = None
    TZ: str | None = None
    DB_URL: str | None = None
    REDIS_URL: str | None = None
    TELEGRAM_MAIN_BOT_TOKEN: str | None = None
    TELEGRAM_AUTH_BOT_TOKEN: str | None = None
    TELEGRAM_WEBHOOK_MAIN_URL: str | None = None
    TELEGRAM_WEBHOOK_AUTH_URL: str | None = None
    TELEGRAM_CHANNEL_ID: str | None = None
    FIRST_SUPERADMIN_TG_ID: int | None = None
    DEFAULT_BROADCAST_RATE_PER_MINUTE: int | None = None
    DEFAULT_BROADCAST_BATCH_SIZE: int | None = None
    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int | None = None
