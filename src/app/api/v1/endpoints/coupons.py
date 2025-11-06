from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.promotions import (
    CouponRepository,
    CouponTemplateRepository,
)
from app.db.repositories.loyalty import ClientRepository, LevelRepository
from app.schemas.promotions import (
    Coupon,
    CouponIssueRequest,
    CouponRedeemRequest,
    CouponRedeemResponse,
)
from app.services.coupons import CouponService
from app.services.loyalty import LoyaltyService
from app.services.redemption import RedemptionService

router = APIRouter()


def get_coupon_service(db: Session = Depends(get_db)) -> CouponService:
    coupon_repository = CouponRepository()
    coupon_template_repository = CouponTemplateRepository()
    client_repository = ClientRepository()
    return CouponService(
        coupon_repository, coupon_template_repository, client_repository
    )


def get_redemption_service(db: Session = Depends(get_db)) -> RedemptionService:
    coupon_repository = CouponRepository()
    client_repository = ClientRepository()
    level_repository = LevelRepository()
    loyalty_service = LoyaltyService(level_repository)
    return RedemptionService(coupon_repository, client_repository, loyalty_service)


@router.post("/issue", response_model=Coupon)
def issue_coupon(
    *,
    issue_request: CouponIssueRequest,
    coupon_service: CouponService = Depends(get_coupon_service),
    db: Session = Depends(get_db),
):
    return coupon_service.issue_coupon(db, issue_request=issue_request)


@router.post("/redeem", response_model=CouponRedeemResponse)
def redeem_coupon(
    *,
    redeem_request: CouponRedeemRequest,
    redemption_service: RedemptionService = Depends(get_redemption_service),
    db: Session = Depends(get_db),
):
    try:
        return redemption_service.redeem_coupon(db, redeem_request=redeem_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
