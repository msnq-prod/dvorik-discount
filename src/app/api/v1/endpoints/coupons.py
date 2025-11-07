from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_event_service
from app.core.exceptions import AppException
from app.db.models.promotions import Coupon
from app.db.repositories.events import CampaignEventRepository
from app.db.repositories.idempotency import IdempotencyRequestRepository
from app.db.repositories.loyalty import ClientRepository, LevelRepository
from app.db.repositories.promotions import (
    CampaignRepository,
    CouponRepository,
    CouponTemplateRepository,
)
from app.schemas.promotions import (
    Coupon as CouponSchema,
    CouponIssueRequest,
    CouponRedeemRequest,
    CouponRedeemResponse,
)
from app.services.coupons import CouponService
from app.services.loyalty import LoyaltyService
from app.services.redemption import RedemptionService

router = APIRouter()


def get_coupon_service(db: Session = Depends(get_db)) -> CouponService:
    return CouponService(
        coupon_repository=CouponRepository(),
        coupon_template_repository=CouponTemplateRepository(),
        client_repository=ClientRepository(),
        campaign_repository=CampaignRepository(),
    )


def get_redemption_service(db: Session = Depends(get_db)) -> RedemptionService:
    return RedemptionService(
        coupon_repository=CouponRepository(),
        client_repository=ClientRepository(),
        campaign_event_repository=CampaignEventRepository(),
        loyalty_service=LoyaltyService(level_repository=LevelRepository()),
        idempotency_request_repository=IdempotencyRequestRepository(),
    )


@router.post(
    "/issue",
    response_model=CouponSchema,
    summary="Issue a new coupon",
)
def issue_coupon(
    *,
    issue_request: CouponIssueRequest,
    coupon_service: CouponService = Depends(get_coupon_service),
    event_service: EventService = Depends(get_event_service),
    db: Session = Depends(get_db),
):
    return coupon_service.issue_coupon(
        db, issue_request=issue_request, event_service=event_service
    )


@router.post(
    "/redeem",
    response_model=CouponRedeemResponse,
    summary="Redeem a coupon",
)
def redeem_coupon(
    *,
    redeem_request: CouponRedeemRequest,
    idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    redemption_service: RedemptionService = Depends(get_redemption_service),
    event_service: EventService = Depends(get_event_service),
    db: Session = Depends(get_db),
):
    try:
        return redemption_service.redeem_coupon(
            db,
            redeem_request=redeem_request,
            event_service=event_service,
            idempotency_key=idempotency_key,
        )
    except AppException as e:
        # This will be caught by the global handler, but keeping it
        # here allows for potential endpoint-specific logic.
        raise HTTPException(status_code=400, detail={"code": e.code, "message": e.message})


@router.get(
    "/by-code/{code}",
    response_model=CouponSchema,
    summary="Get a coupon by its code",
)
def read_coupon_by_code(
    *,
    code: str,
    db: Session = Depends(get_db),
):
    # This should use a repository method
    coupon_repo = CouponRepository()
    coupon = coupon_repo.get_by_code(db, code=code)
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon
