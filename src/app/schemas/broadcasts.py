from datetime import datetime
from typing import Optional

from app.schemas.base import BaseSchema
from app.schemas.enums import BroadcastStatusEnum


class BroadcastBase(BaseSchema):
    name: str
    audience_filter: dict = {}
    content: dict = {}
    schedule_at: Optional[datetime] = None
    status: BroadcastStatusEnum = BroadcastStatusEnum.draft


class BroadcastCreate(BroadcastBase):
    pass


class BroadcastUpdate(BroadcastBase):
    pass


class Broadcast(BroadcastBase):
    id: int
    sent_count: int = 0
    fail_count: int = 0
