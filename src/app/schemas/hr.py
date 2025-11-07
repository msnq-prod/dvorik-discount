from typing import Optional

from app.schemas.base import BaseSchema
from app.schemas.enums import EmployeeRoleEnum


class EmployeeBase(BaseSchema):
    full_name: str
    tg_id: int
    role: EmployeeRoleEnum = EmployeeRoleEnum.cashier
    hourly_rate: float = 0
    active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    id: int
