from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.loyalty import ClientRepository
from app.schemas.loyalty import Client, ClientCreate, ClientUpdate
from app.schemas.promotions import Coupon

router = APIRouter()


def get_client_repository(db: Session = Depends(get_db)) -> ClientRepository:
    return ClientRepository()


@router.get(
    "/by-tg-id/{tg_id}",
    response_model=Client,
    summary="Get a client by Telegram ID",
    description="Retrieves the details of a specific client by their Telegram ID.",
)
def read_client_by_tg_id(
    *,
    tg_id: int,
    client_repo: ClientRepository = Depends(get_client_repository),
    db: Session = Depends(get_db),
):
    client = client_repo.get_by_tg_id(db, tg_id=tg_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("/{client_id}/coupons", response_model=list[Coupon])
def read_client_coupons(
    *,
    client_id: int,
    db: Session = Depends(get_db),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client.coupons


@router.post(
    "/",
    response_model=Client,
    summary="Create a new client",
    description="Creates a new client with the specified details.",
)
def create_client(
    *,
    client_in: ClientCreate,
    client_repo: ClientRepository = Depends(get_client_repository),
    db: Session = Depends(get_db),
):
    return client_repo.create(db, obj_in=client_in)


@router.put(
    "/{client_id}",
    response_model=Client,
    summary="Update a client",
    description="Updates the details of an existing client.",
)
def update_client(
    *,
    client_id: int,
    client_in: ClientUpdate,
    client_repo: ClientRepository = Depends(get_client_repository),
    db: Session = Depends(get_db),
):
    client = client_repo.get(db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client_repo.update(db, db_obj=client, obj_in=client_in)


@router.delete(
    "/{client_id}",
    response_model=Client,
    summary="Delete a client",
    description="Deletes a client by their unique ID.",
)
def delete_client(
    *,
    client_id: int,
    client_repo: ClientRepository = Depends(get_client_repository),
    db: Session = Depends(get_db),
):
    client = client_repo.get(db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client_repo.remove(db, id=client_id)


@router.get(
    "/{client_id}",
    response_model=Client,
    summary="Get a specific client by ID",
    description="Retrieves the details of a specific client by their unique ID.",
)
def read_client(
    *,
    client_id: int,
    client_repo: ClientRepository = Depends(get_client_repository),
    db: Session = Depends(get_db),
):
    client = client_repo.get(db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client
