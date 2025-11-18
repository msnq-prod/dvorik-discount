from datetime import datetime
from typing import Optional

from app.schemas.base import BaseSchema
from app.schemas.enums import ActorTypeEnum


class AuditLogBase(BaseSchema):
    actor_type: ActorTypeEnum
    actor_id: Optional[int] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    payload: dict = {}
    ip: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLog(AuditLogBase):
    id: int
    ts: datetime


class EventBase(BaseSchema):
    name: str
    actor_type: Optional[ActorTypeEnum] = None
    actor_id: Optional[int] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    payload: dict = {}


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    ts: datetime
