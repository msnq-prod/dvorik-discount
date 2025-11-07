from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_audit_service
from app.db.repositories.hr import ShiftRepository
from app.schemas.hr import Shift, ShiftCreate, ShiftUpdate
from app.schemas.events import AuditLogCreate
from app.schemas.enums import ActorTypeEnum
from app.services.shifts import ShiftService
from app.services.events import AuditService

router = APIRouter()


def get_shift_service(db: Session = Depends(get_db)) -> ShiftService:
    shift_repository = ShiftRepository()
    return ShiftService(shift_repository)


@router.post(
    "/",
    response_model=Shift,
    summary="Create a new shift",
    description="Creates a new shift for an employee.",
)
def create_shift(
    *,
    shift_in: ShiftCreate,
    shift_service: ShiftService = Depends(get_shift_service),
    audit_service: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    shift = shift_service.create_shift(db, shift_in=shift_in)
    audit_service.log_action(
        db,
        log_in=AuditLogCreate(
            actor_type=ActorTypeEnum.admin,
            action="create_shift",
            entity_type="shift",
            entity_id=shift.id,
            payload=shift_in.model_dump(),
        ),
    )
    return shift


@router.get(
    "/{shift_id}",
    response_model=Shift,
    summary="Get a specific shift by ID",
    description="Retrieves the details of a specific shift by its unique ID.",
)
def read_shift(
    *,
    shift_id: int,
    shift_service: ShiftService = Depends(get_shift_service),
    db: Session = Depends(get_db),
):
    shift = shift_service.get_shift(db, shift_id=shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


@router.get(
    "/",
    response_model=list[Shift],
    summary="Get all shifts",
    description="Retrieves a list of all shifts.",
)
def read_shifts(
    shift_service: ShiftService = Depends(get_shift_service),
    db: Session = Depends(get_db),
):
    return shift_service.get_all_shifts(db)


@router.put(
    "/{shift_id}",
    response_model=Shift,
    summary="Update a shift",
    description="Updates the details of an existing shift.",
)
def update_shift(
    *,
    shift_id: int,
    shift_in: ShiftUpdate,
    shift_service: ShiftService = Depends(get_shift_service),
    audit_service: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    shift = shift_service.get_shift(db, shift_id=shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    updated_shift = shift_service.update_shift(db, shift=shift, shift_in=shift_in)
    audit_service.log_action(
        db,
        log_in=AuditLogCreate(
            actor_type=ActorTypeEnum.admin,
            action="update_shift",
            entity_type="shift",
            entity_id=shift_id,
            payload=shift_in.model_dump(exclude_unset=True),
        ),
    )
    return updated_shift


@router.delete(
    "/{shift_id}",
    response_model=Shift,
    summary="Delete a shift",
    description="Deletes a shift by its unique ID.",
)
def delete_shift(
    *,
    shift_id: int,
    shift_service: ShiftService = Depends(get_shift_service),
    audit_service: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    shift = shift_service.get_shift(db, shift_id=shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    deleted_shift = shift_service.remove_shift(db, shift_id=shift_id)
    audit_service.log_action(
        db,
        log_in=AuditLogCreate(
            actor_type=ActorTypeEnum.admin,
            action="delete_shift",
            entity_type="shift",
            entity_id=shift_id,
        ),
    )
    return deleted_shift
