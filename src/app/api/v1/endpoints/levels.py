from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.loyalty import LevelRepository
from app.schemas.loyalty import Level, LevelCreate, LevelUpdate
from app.services.loyalty import LoyaltyService

router = APIRouter()


def get_level_service(db: Session = Depends(get_db)) -> LoyaltyService:
    level_repository = LevelRepository()
    return LoyaltyService(level_repository)


@router.post("/", response_model=Level)
def create_level(
    *,
    level_in: LevelCreate,
    level_service: LoyaltyService = Depends(get_level_service),
    db: Session = Depends(get_db),
):
    return level_service.create_level(db, level_in=level_in)


@router.get("/{level_id}", response_model=Level)
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


@router.get("/", response_model=list[Level])
def read_levels(
    level_service: LoyaltyService = Depends(get_level_service),
    db: Session = Depends(get_db),
):
    return level_service.get_all_levels(db)


@router.put("/{level_id}", response_model=Level)
def update_level(
    *,
    level_id: int,
    level_in: LevelUpdate,
    level_service: LoyaltyService = Depends(get_level_service),
    db: Session = Depends(get_db),
):
    level = level_service.get_level(db, level_id=level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    return level_service.update_level(db, level=level, level_in=level_in)


@router.delete("/{level_id}", response_model=Level)
def delete_level(
    *,
    level_id: int,
    level_service: LoyaltyService = Depends(get_level_service),
    db: Session = Depends(get_db),
):
    level = level_service.get_level(db, level_id=level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    return level_service.remove_level(db, level_id=level_id)
