from typing import Optional
from pydantic import Field
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


from datetime import date

class Employee(EmployeeBase):
    id: int


# Shift Schemas
class ShiftBase(BaseSchema):
    employee_id: int
    date: date
    hours: float = Field(..., gt=0)


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(ShiftBase):
    pass


class Shift(ShiftBase):
    id: int


# Payroll Schemas
class PayrollBase(BaseSchema):
    employee_id: int
    month: date
    shifts_count: int
    gross: float
    taxes: float
    net: float


class PayrollCreate(PayrollBase):
    pass


class PayrollUpdate(PayrollBase):
    pass


class Payroll(PayrollBase):
    id: int
