from sqlalchemy.orm import Session

from app.db.repositories.loyalty import ClientRepository
from app.schemas.purchases import PurchaseCreate
from app.services.loyalty import LoyaltyService


class PurchaseService:
    def __init__(
        self,
        client_repository: ClientRepository,
        loyalty_service: LoyaltyService,
    ):
        self.client_repository = client_repository
        self.loyalty_service = loyalty_service

    def record_purchase(self, db: Session, *, purchase_in: PurchaseCreate):
        client = self.client_repository.get_by_identifier(
            db, identifier=purchase_in.client_ref
        )
        if not client:
            raise ValueError("Client not found.")

        client.total_spent += purchase_in.amount
        db.add(client)
        db.commit()

        self.loyalty_service.recalculate_level(db, client=client)
