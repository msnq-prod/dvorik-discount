from app.db.models.hr import Employee, Shift, Payroll
from app.db.repositories.base import BaseRepository
from app.schemas.hr import (
    EmployeeCreate,
    EmployeeUpdate,
    ShiftCreate,
    ShiftUpdate,
    PayrollCreate,
    PayrollUpdate,
)


class EmployeeRepository(BaseRepository[Employee, EmployeeCreate, EmployeeUpdate]):
    def __init__(self):
        super().__init__(Employee)

    def get_by_tg_id(self, db, *, tg_id: int) -> Employee | None:
        return db.query(self.model).filter(self.model.tg_id == tg_id).first()


class ShiftRepository(BaseRepository[Shift, ShiftCreate, ShiftUpdate]):
    def __init__(self):
        super().__init__(Shift)


class PayrollRepository(BaseRepository[Payroll, PayrollCreate, PayrollUpdate]):
    def __init__(self):
        super().__init__(Payroll)
