import random
import string

from sqlalchemy.orm import Session

from app.db.models.promotions import Coupon
from app.db.repositories.promotions import CouponRepository, CouponTemplateRepository
from app.db.repositories.loyalty import ClientRepository
from datetime import datetime, timedelta

from app.core.exceptions import CouponConditionsNotMetException
from app.db.models.loyalty import Client
from app.db.models.promotions import CouponTemplate
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

    def _validate_client_for_template(self, client: Client, template: CouponTemplate):
        conditions = template.conditions
        if not conditions:
            return

        if "min_level" in conditions:
            if not client.level or client.level.order < conditions["min_level"]:
                raise CouponConditionsNotMetException("уровень клиента слишком низкий")

        if "gender" in conditions:
            if client.gender.name != conditions["gender"]:
                raise CouponConditionsNotMetException("пол клиента не соответствует")

        # Further checks for age, tags, etc. can be added here.

    def _calculate_expiration_date(
        self, template: CouponTemplate, requested_date: datetime | None
    ) -> datetime | None:
        if requested_date:
            return requested_date
        if template.expiration_days:
            return datetime.utcnow() + timedelta(days=template.expiration_days)
        return None

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

        self._validate_client_for_template(client, template)

        expires_at = self._calculate_expiration_date(template, issue_request.expires_at)

        coupon_in = CouponCreate(
            code=self._generate_unique_code(db, template.code_pattern),
            template_id=issue_request.template_id,
            client_id=client.id,
            campaign_id=issue_request.campaign_id,
            status="issued",
            expires_at=expires_at,
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
