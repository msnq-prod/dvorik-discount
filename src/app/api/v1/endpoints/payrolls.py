from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.hr import EmployeeRepository
from app.schemas.hr import Payroll
from app.services.payroll import PayrollService

router = APIRouter()


from app.db.repositories.hr import PayrollRepository, ShiftRepository

def get_payroll_service(db: Session = Depends(get_db)) -> PayrollService:
    payroll_repository = PayrollRepository()
    shift_repository = ShiftRepository()
    return PayrollService(payroll_repository, shift_repository)


@router.post(
    "/calculate",
    response_model=Payroll,
    summary="Calculate payroll for an employee",
    description="Calculates payroll for a specific employee for a given month.",
)
def calculate_payroll(
    *,
    employee_id: int,
    month: date,
    payroll_service: PayrollService = Depends(get_payroll_service),
    db: Session = Depends(get_db),
):
    employee_repo = EmployeeRepository()
    employee = employee_repo.get(db, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return payroll_service.calculate_payroll(db, employee=employee, month=month)


@router.get(
    "/",
    response_model=list[Payroll],
    summary="Get all payrolls",
    description="Retrieves a list of all payrolls.",
)
def read_payrolls(
    payroll_service: PayrollService = Depends(get_payroll_service),
    db: Session = Depends(get_db),
):
    return payroll_service.get_all_payrolls(db)
