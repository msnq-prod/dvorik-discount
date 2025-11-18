from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.broadcasts import BroadcastRepository
from app.schemas.broadcasts import Broadcast, BroadcastCreate, BroadcastUpdate
from app.services.broadcasts import BroadcastService

router = APIRouter()


def get_broadcast_service(db: Session = Depends(get_db)) -> BroadcastService:
    broadcast_repository = BroadcastRepository()
    return BroadcastService(broadcast_repository)


@router.post(
    "/",
    response_model=Broadcast,
    summary="Create a new broadcast",
    description="Creates a new broadcast with the specified audience filter and content.",
)
def create_broadcast(
    *,
    broadcast_in: BroadcastCreate,
    broadcast_service: BroadcastService = Depends(get_broadcast_service),
    db: Session = Depends(get_db),
):
    return broadcast_service.create_broadcast(db, broadcast_in=broadcast_in)


@router.get(
    "/{broadcast_id}",
    response_model=Broadcast,
    summary="Get a specific broadcast by ID",
    description="Retrieves the details of a specific broadcast by its unique ID.",
)
def read_broadcast(
    *,
    broadcast_id: int,
    broadcast_service: BroadcastService = Depends(get_broadcast_service),
    db: Session = Depends(get_db),
):
    broadcast = broadcast_service.get_broadcast(db, broadcast_id=broadcast_id)
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    return broadcast


@router.get(
    "/",
    response_model=list[Broadcast],
    summary="Get all broadcasts",
    description="Retrieves a list of all broadcasts.",
)
def read_broadcasts(
    broadcast_service: BroadcastService = Depends(get_broadcast_service),
    db: Session = Depends(get_db),
):
    return broadcast_service.get_all_broadcasts(db)


@router.put(
    "/{broadcast_id}",
    response_model=Broadcast,
    summary="Update a broadcast",
    description="Updates the details of an existing broadcast.",
)
def update_broadcast(
    *,
    broadcast_id: int,
    broadcast_in: BroadcastUpdate,
    broadcast_service: BroadcastService = Depends(get_broadcast_service),
    db: Session = Depends(get_db),
):
    broadcast = broadcast_service.get_broadcast(db, broadcast_id=broadcast_id)
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    return broadcast_service.update_broadcast(
        db, broadcast=broadcast, broadcast_in=broadcast_in
    )


@router.delete(
    "/{broadcast_id}",
    response_model=Broadcast,
    summary="Delete a broadcast",
    description="Deletes a broadcast by its unique ID.",
)
def delete_broadcast(
    *,
    broadcast_id: int,
    broadcast_service: BroadcastService = Depends(get_broadcast_service),
    db: Session = Depends(get_db),
):
    broadcast = broadcast_service.get_broadcast(db, broadcast_id=broadcast_id)
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    return broadcast_service.remove_broadcast(db, broadcast_id=broadcast_id)
