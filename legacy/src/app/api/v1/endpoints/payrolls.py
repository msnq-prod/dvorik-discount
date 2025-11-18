from datetime import date

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_audit_service
from app.db.repositories.hr import EmployeeRepository
from app.schemas.hr import Payroll
from app.schemas.events import AuditLogCreate
from app.schemas.enums import ActorTypeEnum
from app.services.payroll import PayrollService
from app.services.events import AuditService

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
    audit_service: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    employee_repo = EmployeeRepository()
    employee = employee_repo.get(db, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    payroll = payroll_service.calculate_payroll(db, employee=employee, month=month)
    audit_service.log_action(
        db,
        log_in=AuditLogCreate(
            actor_type=ActorTypeEnum.admin,
            action="calculate_payroll",
            entity_type="payroll",
            entity_id=payroll.id,
            payload={"employee_id": employee_id, "month": month.isoformat()},
        ),
    )
    return payroll


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
