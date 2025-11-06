from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.promotions import (
    CouponRepository,
    CouponTemplateRepository,
)
from app.db.repositories.loyalty import ClientRepository
from app.schemas.promotions import Coupon, CouponIssueRequest
from app.services.coupons import CouponService

router = APIRouter()


def get_coupon_service(db: Session = Depends(get_db)) -> CouponService:
    coupon_repository = CouponRepository()
    coupon_template_repository = CouponTemplateRepository()
    client_repository = ClientRepository()
    return CouponService(
        coupon_repository, coupon_template_repository, client_repository
    )


@router.post("/issue", response_model=Coupon)
def issue_coupon(
    *,
    issue_request: CouponIssueRequest,
    coupon_service: CouponService = Depends(get_coupon_service),
    db: Session = Depends(get_db),
):
    return coupon_service.issue_coupon(db, issue_request=issue_request)
