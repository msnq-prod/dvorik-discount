from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ClientNotFoundException,
    CouponAlreadyRedeemedException,
    CouponClientMismatchException,
    CouponConditionsNotMetException,
    CouponExpiredException,
    CouponInvalidStatusException,
    CouponMinPurchaseNotMetException,
    CouponNotFoundException,
    CouponPerUserLimitExceededException,
    CouponUsageLimitExceededException,
)
from app.db.models.loyalty import Client
from app.db.models.promotions import Coupon, CouponTemplate
from app.db.repositories.events import CampaignEventRepository
from app.db.repositories.loyalty import ClientRepository
from app.db.repositories.promotions import CouponRepository
from app.schemas.enums import CouponStatusEnum, DiscountTypeEnum
from app.schemas.events import EventCreate
from app.schemas.enums import ActorTypeEnum, EventNameEnum
from app.schemas.promotions import (
    CouponRedeemRequest,
    CouponRedeemResponse,
    RedemptionResult,
)
from app.services.events import EventService
from app.services.loyalty import LoyaltyService


class RedemptionService:
    def __init__(
        self,
        coupon_repository: CouponRepository,
        client_repository: ClientRepository,
        campaign_event_repository: CampaignEventRepository,
        loyalty_service: LoyaltyService,
    ):
        self.coupon_repository = coupon_repository
        self.client_repository = client_repository
        self.campaign_event_repository = campaign_event_repository
        self.loyalty_service = loyalty_service

    def _get_client(self, db: Session, client_ref: str) -> Client:
        client = self.client_repository.get_by_identifier(db, identifier=client_ref)
        if not client:
            raise ClientNotFoundException(client_ref=client_ref)
        return client

    def _get_coupon_for_update(self, db: Session, code: str) -> Coupon:
        coupon = self.coupon_repository.get_by_code_for_update(db, code=code)
        if not coupon:
            raise CouponNotFoundException(code_or_id=code)
        return coupon

    def _validate_coupon(
        self, coupon: Coupon, client: Client, amount: float
    ) -> None:
        if coupon.status == CouponStatusEnum.redeemed:
            raise CouponAlreadyRedeemedException()
        if coupon.status not_in (CouponStatusEnum.active, CouponStatusEnum.issued):
            raise CouponInvalidStatusException(status=coupon.status.name)
        if coupon.expires_at and coupon.expires_at < datetime.utcnow():
            raise CouponExpiredException()
        if coupon.client_id and coupon.client_id != client.id:
            raise CouponClientMismatchException()

        template = coupon.template
        if template.min_purchase and amount < template.min_purchase:
            raise CouponMinPurchaseNotMetException(
                min_purchase=template.min_purchase, amount=amount
            )

        # Basic condition check (can be expanded)
        if "min_level" in template.conditions:
            if not client.level or client.level.order < template.conditions["min_level"]:
                raise CouponConditionsNotMetException("уровень клиента слишком низкий")

    def _check_usage_limits(self, db: Session, coupon: Coupon, client: Client) -> None:
        template = coupon.template
        if not template.usage_limit and not template.per_user_limit:
            return

        if template.usage_limit:
            total_usages = (
                self.campaign_event_repository.get_redeem_count_for_coupon(
                    db, coupon_id=coupon.id
                )
            )
            if total_usages >= template.usage_limit:
                raise CouponUsageLimitExceededException()

        if template.per_user_limit:
            user_usages = (
                self.campaign_event_repository.get_redeem_count_for_client_and_template(
                    db, client_id=client.id, template_id=coupon.template_id
                )
            )
            if user_usages >= template.per_user_limit:
                raise CouponPerUserLimitExceededException()

    def _calculate_discount(self, template: CouponTemplate, amount: float) -> float:
        if template.discount_type == DiscountTypeEnum.percent:
            return round(amount * template.discount_value / 100, 2)
        if template.discount_type == DiscountTypeEnum.fixed:
            return min(template.discount_value, amount)
        return 0.0

    def _apply_stacking_rules(
        self,
        coupon_discount: float,
        client: Client,
        template: CouponTemplate,
        amount: float,
    ) -> float:
        # Currently, only coupon discount is supported.
        # Level-based discounts are not yet in perks.
        # This is a placeholder for future stacking logic.
        total_discount = coupon_discount

        rules = template.stacking_rules
        if not rules.get("allow_sum", False):
            return total_discount

        min_level_required = rules.get("min_level")
        if min_level_required and (not client.level or client.level.order < min_level_required):
            return total_discount

        # Placeholder for level perks discount
        level_discount = 0.0
        # if client.level and "percent_discount" in client.level.perks:
        #    level_discount = round(amount * client.level.perks["percent_discount"] / 100, 2)

        total_discount += level_discount

        max_discount_percent = rules.get("max_total_discount_percent")
        if max_discount_percent:
            max_discount_value = round(amount * max_discount_percent / 100, 2)
            total_discount = min(total_discount, max_discount_value)

        return total_discount

    def _redeem_one_time_coupon(
        self, db: Session, coupon: Coupon, request: CouponRedeemRequest
    ) -> None:
        coupon.status = CouponStatusEnum.redeemed
        coupon.redeemed_at = datetime.utcnow()
        coupon.redeemed_by_employee_id = request.employee_id
        coupon.redemption_amount = request.amount
        db.add(coupon)

    def _touch_multi_use_coupon(self, db: Session, coupon: Coupon) -> None:
        coupon.redeemed_at = datetime.utcnow()  # Mark last usage time
        db.add(coupon)

    def redeem_coupon(
        self,
        db: Session,
        *,
        redeem_request: CouponRedeemRequest,
        event_service: EventService,
    ) -> CouponRedeemResponse:
        client = self._get_client(db, client_ref=redeem_request.client_ref)

        with db.begin_nested():
            coupon = self._get_coupon_for_update(db, code=redeem_request.code)
            self._validate_coupon(coupon, client, redeem_request.amount)
            self._check_usage_limits(db, coupon, client)

            coupon_discount = self._calculate_discount(coupon.template, redeem_request.amount)
            discount = self._apply_stacking_rules(
                coupon_discount, client, coupon.template, redeem_request.amount
            )
            payable = max(redeem_request.amount - discount, 0)

            # Record redemption event
            event_service.record_event(
                db,
                event_in=EventCreate(
                    name=EventNameEnum.COUPON_REDEEMED,
                    actor_type=ActorTypeEnum.employee,
                    actor_id=redeem_request.employee_id,
                    entity_type="coupon",
                    entity_id=coupon.id,
                    payload={
                        "client_id": client.id,
                        "amount": redeem_request.amount,
                        "discount": discount,
                    },
                ),
            )

            # Update coupon status
            is_one_time = not coupon.template.usage_limit
            if is_one_time:
                self._redeem_one_time_coupon(db, coupon, redeem_request)
            else:
                self._touch_multi_use_coupon(db, coupon)

            # Update client's total spent and recalculate level
            client.total_spent += redeem_request.amount
            db.add(client)
            self.loyalty_service.recalculate_level(db, client=client)

            db.commit()

        db.refresh(client)
        return CouponRedeemResponse(
            result=RedemptionResult(
                code=coupon.code,
                amount=redeem_request.amount,
                discount=discount,
                payable=payable,
                status=coupon.status,
                redeemed_at=coupon.redeemed_at,
            ),
            client=client,
        )

    def record_purchase_without_coupon(
        self,
        db: Session,
        *,
        client_ref: str,
        amount: float,
        employee_id: int,
        event_service: EventService,
    ) -> Client:
        client = self._get_client(db, client_ref=client_ref)
        client.total_spent += amount
        self.loyalty_service.recalculate_level(db, client=client)
        db.add(client)

        event_service.record_event(
            db,
            event_in=EventCreate(
                name=EventNameEnum.PURCHASE_RECORDED,
                actor_type=ActorTypeEnum.employee,
                actor_id=employee_id,
                entity_type="client",
                entity_id=client.id,
                payload={"amount": amount},
            ),
        )

        db.commit()
        db.refresh(client)
        return client
