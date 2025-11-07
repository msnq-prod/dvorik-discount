import random
import string
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ClientNotFoundException,
    CouponConditionsNotMetException,
    CouponTemplateNotFoundException,
    AppException,
)
from app.db.models.loyalty import Client
from app.db.models.promotions import Campaign, Coupon, CouponTemplate
from app.db.repositories.loyalty import ClientRepository
from app.db.repositories.promotions import (
    CampaignRepository,
    CouponRepository,
    CouponTemplateRepository,
)
from app.schemas.enums import ActorTypeEnum, EventNameEnum
from app.schemas.events import EventCreate
from app.schemas.promotions import CouponCreate, CouponIssueRequest
from app.services.events import EventService


class CampaignMissingCodePrefixException(AppException):
    def __init__(self, campaign_id: int):
        super().__init__(
            code="E-CAMP-NO-PREFIX",
            message="Для кампании не задан префикс кода купона.",
            details={"campaign_id": campaign_id},
        )


class CouponService:
    def __init__(
        self,
        coupon_repository: CouponRepository,
        coupon_template_repository: CouponTemplateRepository,
        client_repository: ClientRepository,
        campaign_repository: CampaignRepository,
    ):
        self.coupon_repository = coupon_repository
        self.coupon_template_repository = coupon_template_repository
        self.client_repository = client_repository
        self.campaign_repository = campaign_repository

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

    def _calculate_expiration_date(
        self, template: CouponTemplate, requested_date: Optional[datetime]
    ) -> Optional[datetime]:
        if requested_date:
            return requested_date
        if template.expiration_days:
            return datetime.utcnow() + timedelta(days=template.expiration_days)
        return None

    def _generate_unique_code(self, db: Session, prefix: str) -> str:
        while True:
            random_part = "".join(random.choices(string.digits, k=5))
            code = f"{prefix}-{random_part}"
            if not self.coupon_repository.get_by_code(db, code=code):
                return code

    def issue_coupon(
        self,
        db: Session,
        *,
        issue_request: CouponIssueRequest,
        event_service: EventService,
    ) -> Coupon:
        template = self.coupon_template_repository.get(
            db, id=issue_request.template_id
        )
        if not template:
            raise CouponTemplateNotFoundException(template_id=issue_request.template_id)

        client = self.client_repository.get_by_identifier(
            db, identifier=issue_request.client_ref
        )
        if not client:
            raise ClientNotFoundException(client_ref=issue_request.client_ref)

        campaign: Optional[Campaign] = None
        if issue_request.campaign_id:
            campaign = self.campaign_repository.get(db, id=issue_request.campaign_id)
            if not campaign:
                # This should ideally be a more specific exception
                raise ValueError("Campaign not found")
            if not campaign.code_prefix:
                raise CampaignMissingCodePrefixException(campaign_id=campaign.id)
            code_prefix = campaign.code_prefix
        else:
            # Fallback to template pattern if no campaign is specified
            code_prefix = template.code_pattern.split("-")[0]

        self._validate_client_for_template(client, template)

        expires_at = self._calculate_expiration_date(
            template, issue_request.expires_at
        )

        coupon_in = CouponCreate(
            code=self._generate_unique_code(db, prefix=code_prefix),
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
