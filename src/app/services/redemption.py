from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.promotions import Coupon
from app.db.repositories.loyalty import ClientRepository
from app.db.repositories.promotions import CouponRepository
from app.schemas.enums import CouponStatusEnum, DiscountTypeEnum
from app.schemas.promotions import CouponRedeemRequest, CouponRedeemResponse
from app.schemas.events import EventCreate
from app.schemas.enums import ActorTypeEnum, EventNameEnum
from app.services.events import EventService
from app.services.loyalty import LoyaltyService


class RedemptionService:
    def __init__(
        self,
        coupon_repository: CouponRepository,
        client_repository: ClientRepository,
        loyalty_service: LoyaltyService,
    ):
        self.coupon_repository = coupon_repository
        self.client_repository = client_repository
        self.loyalty_service = loyalty_service

    def _calculate_discount(self, *, coupon: Coupon, amount: float) -> float:
        template = coupon.template
        if template.discount_type == DiscountTypeEnum.percent:
            return round(amount * template.discount_value / 100, 2)
        elif template.discount_type == DiscountTypeEnum.fixed:
            return min(template.discount_value, amount)
        return 0.0

    def redeem_coupon(
        self,
        db: Session,
        *,
        redeem_request: CouponRedeemRequest,
        event_service: EventService,
    ) -> CouponRedeemResponse:
        with db.begin_nested():
            coupon = (
                db.query(Coupon)
                .filter(Coupon.code == redeem_request.code)
                .with_for_update()
                .first()
            )

            if not coupon:
                raise ValueError("Invalid coupon code.")
            if coupon.status != CouponStatusEnum.issued:
                raise ValueError(f"Coupon is not active. Status: {coupon.status}")
            if coupon.expires_at and coupon.expires_at < datetime.utcnow():
                raise ValueError("Coupon has expired.")

            client = self.client_repository.get_by_identifier(
                db, identifier=redeem_request.client_ref
            )
            if not client:
                raise ValueError("Client not found.")
            if coupon.client_id != client.id:
                raise ValueError("Coupon does not belong to this client.")

            discount = self._calculate_discount(
                coupon=coupon, amount=redeem_request.amount
            )
            payable = max(redeem_request.amount - discount, 0)

            coupon.status = CouponStatusEnum.redeemed
            coupon.redeemed_at = datetime.utcnow()
            coupon.redeemed_by_employee_id = redeem_request.employee_id
            coupon.redemption_amount = redeem_request.amount
            db.add(coupon)

            client.total_spent += redeem_request.amount
            db.add(client)

            self.loyalty_service.recalculate_level(db, client=client)

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

            db.commit()

        return CouponRedeemResponse(
            code=coupon.code,
            amount=redeem_request.amount,
            discount=discount,
            payable=payable,
            status=coupon.status,
            redeemed_at=coupon.redeemed_at,
        )
