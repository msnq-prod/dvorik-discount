from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.events import EventRepository
from app.schemas.events import Event

router = APIRouter()


def get_event_repository(db: Session = Depends(get_db)) -> EventRepository:
    return EventRepository(db=db)


@router.get(
    "/",
    response_model=list[Event],
    summary="Get all events",
    description="Retrieves a list of all business events, with optional pagination.",
)
def read_events(
    skip: int = 0,
    limit: int = 100,
    event_repo: EventRepository = Depends(get_event_repository),
) -> Any:
    """
    Retrieve events.
    """
    return event_repo.get_multi(skip=skip, limit=limit)
