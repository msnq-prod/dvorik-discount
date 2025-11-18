from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_audit_service
from app.db.repositories.loyalty import LevelRepository
from app.schemas.loyalty import Level, LevelCreate, LevelUpdate
from app.schemas.events import AuditLogCreate
from app.schemas.enums import ActorTypeEnum
from app.services.loyalty import LoyaltyService
from app.services.events import AuditService

router = APIRouter()


def get_level_service(db: Session = Depends(get_db)) -> LoyaltyService:
    level_repository = LevelRepository()
    return LoyaltyService(level_repository)


@router.post(
    "/",
    response_model=Level,
    summary="Create a new loyalty level",
    description="Creates a new loyalty level with a name, threshold, and perks.",
)
def create_level(
    *,
    level_in: LevelCreate,
    level_service: LoyaltyService = Depends(get_level_service),
    audit_service: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    level = level_service.create_level(db, level_in=level_in)
    audit_service.log_action(
        db,
        log_in=AuditLogCreate(
            actor_type=ActorTypeEnum.admin,
            action="create_level",
            entity_type="level",
            entity_id=level.id,
            payload=level_in.model_dump(),
        ),
    )
    return level


@router.get(
    "/{level_id}",
    response_model=Level,
    summary="Get a specific loyalty level by ID",
    description="Retrieves the details of a specific loyalty level by its unique ID.",
)
def read_level(
    *,
    level_id: int,
    level_service: LoyaltyService = Depends(get_level_service),
    db: Session = Depends(get_db),
):
    level = level_service.get_level(db, level_id=level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    return level


@router.get(
    "/",
    response_model=list[Level],
    summary="Get all loyalty levels",
    description="Retrieves a list of all loyalty levels.",
)
def read_levels(
    level_service: LoyaltyService = Depends(get_level_service),
    db: Session = Depends(get_db),
):
    return level_service.get_all_levels(db)


@router.put(
    "/{level_id}",
    response_model=Level,
    summary="Update a loyalty level",
    description="Updates the details of an existing loyalty level.",
)
def update_level(
    *,
    level_id: int,
    level_in: LevelUpdate,
    level_service: LoyaltyService = Depends(get_level_service),
    audit_service: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    level = level_service.get_level(db, level_id=level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    updated_level = level_service.update_level(db, level=level, level_in=level_in)
    audit_service.log_action(
        db,
        log_in=AuditLogCreate(
            actor_type=ActorTypeEnum.admin,
            action="update_level",
            entity_type="level",
            entity_id=level_id,
            payload=level_in.model_dump(),
        ),
    )
    return updated_level


@router.delete(
    "/{level_id}",
    response_model=Level,
    summary="Delete a loyalty level",
    description="Deletes a loyalty level by its unique ID.",
)
def delete_level(
    *,
    level_id: int,
    level_service: LoyaltyService = Depends(get_level_service),
    audit_service: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    level = level_service.get_level(db, level_id=level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    deleted_level = level_service.remove_level(db, level_id=level_id)
    audit_service.log_action(
        db,
        log_in=AuditLogCreate(
            actor_type=ActorTypeEnum.admin,
            action="delete_level",
            entity_type="level",
            entity_id=level_id,
        ),
    )
    return deleted_level
