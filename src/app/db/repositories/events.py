from sqlalchemy.orm import Session

from app.db.models.events import AuditLog, Broadcast, CampaignEvent, Event, Subscription
from app.db.models.promotions import Coupon
from app.db.repositories.base import BaseRepository
from app.schemas.broadcasts import BroadcastCreate, BroadcastUpdate
from app.schemas.enums import CampaignEventTypeEnum
from app.schemas.events import (
    AuditLogCreate,
    EventCreate,
    SubscriptionCreate,
    SubscriptionUpdate,
)


class BroadcastRepository(BaseRepository[Broadcast, BroadcastCreate, BroadcastUpdate]):
    def __init__(self):
        super().__init__(Broadcast)


class AuditLogRepository(BaseRepository[AuditLog, AuditLogCreate, AuditLogCreate]):
    def __init__(self):
        super().__init__(AuditLog)


class EventRepository(BaseRepository[Event, EventCreate, EventCreate]):
    def __init__(self):
        super().__init__(Event)


class CampaignEventRepository(BaseRepository[CampaignEvent, EventCreate, EventCreate]):
    def __init__(self):
        super().__init__(CampaignEvent)

    def get_redeem_count_for_coupon(self, db: Session, *, coupon_id: int) -> int:
        return (
            db.query(self.model)
            .filter(
                self.model.coupon_id == coupon_id,
                self.model.type == CampaignEventTypeEnum.redeem,
            )
            .count()
        )

    def get_redeem_count_for_client_and_template(
        self, db: Session, *, client_id: int, template_id: int
    ) -> int:
        # This join is incorrect in the original thought, let's fix it
        return (
            db.query(self.model)
            .join(Coupon, self.model.coupon_id == Coupon.id)
            .filter(
                self.model.client_id == client_id,
                Coupon.template_id == template_id,
                self.model.type == CampaignEventTypeEnum.redeem,
            )
            .count()
        )


class SubscriptionRepository(
    BaseRepository[Subscription, SubscriptionCreate, SubscriptionUpdate]
):
    def __init__(self):
        super().__init__(Subscription)
