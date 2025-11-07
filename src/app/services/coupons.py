import random
import string

from sqlalchemy.orm import Session

from app.db.models.promotions import Coupon
from app.db.repositories.promotions import CouponRepository, CouponTemplateRepository
from app.db.repositories.loyalty import ClientRepository
from app.schemas.promotions import CouponCreate, CouponIssueRequest
from app.schemas.events import EventCreate
from app.schemas.enums import ActorTypeEnum, EventNameEnum
from app.services.events import EventService


class CouponService:
    def __init__(
        self,
        coupon_repository: CouponRepository,
        coupon_template_repository: CouponTemplateRepository,
        client_repository: ClientRepository,
    ):
        self.coupon_repository = coupon_repository
        self.coupon_template_repository = coupon_template_repository
        self.client_repository = client_repository

    def _generate_unique_code(self, db: Session, code_pattern: str) -> str:
        prefix = code_pattern.split("-")[0]
        while True:
            random_part = "".join(random.choices(string.digits, k=5))
            code = f"{prefix}-{random_part}"
            if not db.query(Coupon).filter(Coupon.code == code).first():
                return code

    def issue_coupon(
        self, db: Session, *, issue_request: CouponIssueRequest, event_service: EventService
    ) -> Coupon:
        template = self.coupon_template_repository.get(
            db, id=issue_request.template_id
        )
        if not template:
            raise ValueError("Coupon template not found.")

        client = self.client_repository.get_by_identifier(
            db, identifier=issue_request.client_ref
        )
        if not client:
            raise ValueError("Client not found.")

        coupon_in = CouponCreate(
            code=self._generate_unique_code(db, template.code_pattern),
            template_id=issue_request.template_id,
            client_id=client.id,
            campaign_id=issue_request.campaign_id,
            status="issued",
            expires_at=issue_request.expires_at,
        )
        coupon = self.coupon_repository.create(db, obj_in=coupon_in)

        event_service.record_event(
            db,
            event_in=EventCreate(
                name=EventNameEnum.COUPON_ISSUED,
                actor_type=ActorTypeEnum.bot,
                entity_type="coupon",
                entity_id=coupon.id,
                payload={
                    "client_id": client.id,
                    "campaign_id": coupon.campaign_id,
                    "template_id": coupon.template_id,
                },
            ),
        )

        return coupon
