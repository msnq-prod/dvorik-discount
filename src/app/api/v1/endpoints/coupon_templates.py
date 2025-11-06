from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.promotions import CouponTemplateRepository
from app.schemas.promotions import (
    CouponTemplate,
    CouponTemplateCreate,
    CouponTemplateUpdate,
)
from app.services.coupon_templates import CouponTemplateService

router = APIRouter()


def get_coupon_template_service(
    db: Session = Depends(get_db),
) -> CouponTemplateService:
    coupon_template_repository = CouponTemplateRepository()
    return CouponTemplateService(coupon_template_repository)


@router.post("/", response_model=CouponTemplate)
def create_coupon_template(
    *,
    coupon_template_in: CouponTemplateCreate,
    coupon_template_service: CouponTemplateService = Depends(
        get_coupon_template_service
    ),
    db: Session = Depends(get_db),
):
    return coupon_template_service.create_coupon_template(
        db, coupon_template_in=coupon_template_in
    )


@router.get("/{coupon_template_id}", response_model=CouponTemplate)
def read_coupon_template(
    *,
    coupon_template_id: int,
    coupon_template_service: CouponTemplateService = Depends(
        get_coupon_template_service
    ),
    db: Session = Depends(get_db),
):
    coupon_template = coupon_template_service.get_coupon_template(
        db, coupon_template_id=coupon_template_id
    )
    if not coupon_template:
        raise HTTPException(status_code=404, detail="Coupon template not found")
    return coupon_template


@router.get("/", response_model=list[CouponTemplate])
def read_coupon_templates(
    coupon_template_service: CouponTemplateService = Depends(
        get_coupon_template_service
    ),
    db: Session = Depends(get_db),
):
    return coupon_template_service.get_all_coupon_templates(db)


@router.put("/{coupon_template_id}", response_model=CouponTemplate)
def update_coupon_template(
    *,
    coupon_template_id: int,
    coupon_template_in: CouponTemplateUpdate,
    coupon_template_service: CouponTemplateService = Depends(
        get_coupon_template_service
    ),
    db: Session = Depends(get_db),
):
    coupon_template = coupon_template_service.get_coupon_template(
        db, coupon_template_id=coupon_template_id
    )
    if not coupon_template:
        raise HTTPException(status_code=404, detail="Coupon template not found")
    return coupon_template_service.update_coupon_template(
        db, coupon_template=coupon_template, coupon_template_in=coupon_template_in
    )


@router.delete("/{coupon_template_id}", response_model=CouponTemplate)
def delete_coupon_template(
    *,
    coupon_template_id: int,
    coupon_template_service: CouponTemplateService = Depends(
        get_coupon_template_service
    ),
    db: Session = Depends(get_db),
):
    coupon_template = coupon_template_service.get_coupon_template(
        db, coupon_template_id=coupon_template_id
    )
    if not coupon_template:
        raise HTTPException(status_code=404, detail="Coupon template not found")
    return coupon_template_service.remove_coupon_template(
        db, coupon_template_id=coupon_template_id
    )
