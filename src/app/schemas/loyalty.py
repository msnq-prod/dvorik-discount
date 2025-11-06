from datetime import date
from typing import Optional

from app.schemas.base import BaseSchema
from app.schemas.enums import GenderEnum


class ClientBase(BaseSchema):
    tg_id: Optional[int] = None
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    gender: GenderEnum = GenderEnum.unknown
    identifier: Optional[str] = None
    level_id: Optional[int] = None
    total_spent: float = 0
    tags: dict = {}
    is_subscribed: bool = False
    consents: dict = {}


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class Client(ClientBase):
    id: int
