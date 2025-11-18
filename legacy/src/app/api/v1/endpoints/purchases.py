from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_event_service
from app.schemas.purchases import PurchaseCreate
from app.services.events import EventService
from app.services.purchases import PurchaseService

router = APIRouter()


from app.db.repositories.loyalty import ClientRepository, LevelRepository
from app.services.loyalty import LoyaltyService

def get_purchase_service(db: Session = Depends(get_db)) -> PurchaseService:
    client_repository = ClientRepository()
    level_repository = LevelRepository()
    loyalty_service = LoyaltyService(level_repository)
    return PurchaseService(
        client_repository=client_repository, loyalty_service=loyalty_service
    )


@router.post("/", status_code=201)
def create_purchase(
    *,
    purchase_in: PurchaseCreate,
    purchase_service: PurchaseService = Depends(get_purchase_service),
    event_service: EventService = Depends(get_event_service),
    db: Session = Depends(get_db),
):
    try:
        purchase_service.record_purchase(
            db, purchase_in=purchase_in, event_service=event_service
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
