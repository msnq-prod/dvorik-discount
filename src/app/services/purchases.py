from sqlalchemy.orm import Session

from app.db.repositories.loyalty import ClientRepository
from app.schemas.purchases import PurchaseCreate
from app.schemas.events import EventCreate
from app.schemas.enums import ActorTypeEnum, EventNameEnum
from app.services.events import EventService
from app.services.loyalty import LoyaltyService


class PurchaseService:
    def __init__(
        self,
        client_repository: ClientRepository,
        loyalty_service: LoyaltyService,
    ):
        self.client_repository = client_repository
        self.loyalty_service = loyalty_service

    def record_purchase(
        self, db: Session, *, purchase_in: PurchaseCreate, event_service: EventService
    ):
        client = self.client_repository.get_by_identifier(
            db, identifier=purchase_in.client_ref
        )
        if not client:
            raise ValueError("Client not found.")

        with db.begin_nested():
            client.total_spent += purchase_in.amount
            db.add(client)

            event_service.record_event(
                db,
                event_in=EventCreate(
                    name=EventNameEnum.PURCHASE_RECORDED,
                    actor_type=ActorTypeEnum.employee,
                    actor_id=purchase_in.employee_id,
                    entity_type="client",
                    entity_id=client.id,
                    payload={"amount": purchase_in.amount},
                ),
            )

            self.loyalty_service.recalculate_level(db, client=client)

            db.commit()
