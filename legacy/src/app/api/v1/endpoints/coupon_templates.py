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


@router.post(
    "/",
    response_model=CouponTemplate,
    summary="Create a new coupon template",
    description="Creates a new template for generating coupons.",
)
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


@router.get(
    "/{coupon_template_id}",
    response_model=CouponTemplate,
    summary="Get a specific coupon template by ID",
    description="Retrieves the details of a specific coupon template by its unique ID.",
)
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


@router.get(
    "/",
    response_model=list[CouponTemplate],
    summary="Get all coupon templates",
    description="Retrieves a list of all coupon templates.",
)
def read_coupon_templates(
    coupon_template_service: CouponTemplateService = Depends(
        get_coupon_template_service
    ),
    db: Session = Depends(get_db),
):
    return coupon_template_service.get_all_coupon_templates(db)


@router.put(
    "/{coupon_template_id}",
    response_model=CouponTemplate,
    summary="Update a coupon template",
    description="Updates the details of an existing coupon template.",
)
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


@router.delete(
    "/{coupon_template_id}",
    response_model=CouponTemplate,
    summary="Delete a coupon template",
    description="Deletes a coupon template by its unique ID.",
)
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
