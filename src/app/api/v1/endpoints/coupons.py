from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.promotions import Coupon
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


@router.post(
    "/issue",
    response_model=Coupon,
    summary="Issue a new coupon",
    description="Issues a new coupon to a client based on a template and campaign.",
)
def issue_coupon(
    *,
    issue_request: CouponIssueRequest,
    coupon_service: CouponService = Depends(get_coupon_service),
    db: Session = Depends(get_db),
):
    return coupon_service.issue_coupon(db, issue_request=issue_request)


@router.post(
    "/redeem",
    response_model=CouponRedeemResponse,
    summary="Redeem a coupon",
    description="Redeems a coupon for a purchase, calculates the discount, and updates the client's loyalty status.",
)
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


@router.get(
    "/by-code/{code}",
    response_model=Coupon,
    summary="Get a coupon by its code",
    description="Retrieves the details of a specific coupon by its unique code.",
)
def read_coupon_by_code(
    *,
    code: str,
    db: Session = Depends(get_db),
):
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon
