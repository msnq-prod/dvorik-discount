from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_audit_service
from app.db.repositories.hr import EmployeeRepository
from app.schemas.hr import Employee, Shift, EmployeeCreate, EmployeeUpdate
from app.schemas.events import AuditLogCreate
from app.schemas.enums import ActorTypeEnum
from app.services.events import AuditService

router = APIRouter()


def get_employee_repository(db: Session = Depends(get_db)) -> EmployeeRepository:
    # This is a bit of a hack to reuse the same repository instance
    # within the same request.
    # A better approach would be to use a dependency injection container.
    return EmployeeRepository(db=db)


@router.get(
    "/by-tg-id/{tg_id}",
    response_model=Employee,
    summary="Get an employee by Telegram ID",
    description="Retrieves the details of a specific employee by their Telegram ID.",
)
def read_employee_by_tg_id(
    *,
    tg_id: int,
    employee_repo: EmployeeRepository = Depends(get_employee_repository),
    db: Session = Depends(get_db),
):
    employee = employee_repo.get_by_tg_id(db, tg_id=tg_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post(
    "/",
    response_model=Employee,
    summary="Create a new employee",
    description="Creates a new employee with the specified details.",
)
def create_employee(
    *,
    employee_in: EmployeeCreate,
    employee_repo: EmployeeRepository = Depends(get_employee_repository),
    audit_service: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    employee = employee_repo.create(db, obj_in=employee_in)
    audit_service.log_action(
        db,
        log_in=AuditLogCreate(
            actor_type=ActorTypeEnum.admin,
            action="create_employee",
            entity_type="employee",
            entity_id=employee.id,
            payload=employee_in.model_dump(),
        ),
    )
    return employee


@router.put(
    "/{employee_id}",
    response_model=Employee,
    summary="Update an employee",
    description="Updates the details of an existing employee.",
)
def update_employee(
    *,
    employee_id: int,
    employee_in: EmployeeUpdate,
    employee_repo: EmployeeRepository = Depends(get_employee_repository),
    audit_service: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    employee = employee_repo.get(db, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    updated_employee = employee_repo.update(db, db_obj=employee, obj_in=employee_in)
    audit_service.log_action(
        db,
        log_in=AuditLogCreate(
            actor_type=ActorTypeEnum.admin,
            action="update_employee",
            entity_type="employee",
            entity_id=employee_id,
            payload=employee_in.model_dump(),
        ),
    )
    return updated_employee


@router.delete(
    "/{employee_id}",
    response_model=Employee,
    summary="Delete an employee",
    description="Deletes an employee by their unique ID.",
)
def delete_employee(
    *,
    employee_id: int,
    employee_repo: EmployeeRepository = Depends(get_employee_repository),
    audit_service: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    employee = employee_repo.get(db, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    deleted_employee = employee_repo.remove(db, id=employee_id)
    audit_service.log_action(
        db,
        log_in=AuditLogCreate(
            actor_type=ActorTypeEnum.admin,
            action="delete_employee",
            entity_type="employee",
            entity_id=employee_id,
        ),
    )
    return deleted_employee


@router.get(
    "/{employee_id}/shifts",
    response_model=list[Shift],
    summary="Get shifts for an employee",
    description="Retrieves a list of all shifts for a specific employee.",
)
def read_employee_shifts(
    *,
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee.shifts
