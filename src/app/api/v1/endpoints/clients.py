from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.loyalty import ClientRepository
from app.schemas.loyalty import Client

router = APIRouter()


def get_client_repository(db: Session = Depends(get_db)) -> ClientRepository:
    return ClientRepository()


@router.get("/by-tg-id/{tg_id}", response_model=Client)
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


@router.post("/", response_model=Client)
def create_client(
    *,
    client_in: ClientCreate,
    client_repo: ClientRepository = Depends(get_client_repository),
    db: Session = Depends(get_db),
):
    return client_repo.create(db, obj_in=client_in)


@router.put("/{client_id}", response_model=Client)
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


@router.delete("/{client_id}", response_model=Client)
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


@router.get("/{client_id}", response_model=Client)
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
