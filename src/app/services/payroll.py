from datetime import date, timedelta

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.db.models.hr import Employee, Shift, Payroll
from app.db.repositories.hr import PayrollRepository, ShiftRepository
from app.schemas.hr import PayrollCreate


class PayrollService:
    def __init__(
        self,
        payroll_repository: PayrollRepository,
        shift_repository: ShiftRepository,
    ):
        self.payroll_repository = payroll_repository
        self.shift_repository = shift_repository

    def get_all_payrolls(self, db: Session) -> list[Payroll]:
        return self.payroll_repository.get_all(db)

    def calculate_payroll(
        self, db: Session, *, employee: Employee, month: date
    ) -> Payroll:
        start_date = month.replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        shifts = db.scalars(
            select(Shift).where(
                and_(
                    Shift.employee_id == employee.id,
                    Shift.date.between(start_date, end_date),
                )
            )
        ).all()

        shifts_count = len(shifts)
        total_hours = sum(shift.hours for shift in shifts)
        gross = total_hours * employee.hourly_rate
        taxes = gross * 0.13  # Placeholder for tax calculation
        net = gross - taxes

        payroll_in = PayrollCreate(
            employee_id=employee.id,
            month=start_date,
            shifts_count=shifts_count,
            gross=gross,
            taxes=taxes,
            net=net,
        )
        return self.payroll_repository.create(db, obj_in=payroll_in)
