from sqlalchemy.orm import Session

from app.db.models.promotions import CouponTemplate
from app.db.repositories.promotions import CouponTemplateRepository
from app.schemas.promotions import CouponTemplateCreate, CouponTemplateUpdate


class CouponTemplateService:
    def __init__(self, coupon_template_repository: CouponTemplateRepository):
        self.coupon_template_repository = coupon_template_repository

    def create_coupon_template(
        self, db: Session, *, coupon_template_in: CouponTemplateCreate
    ) -> CouponTemplate:
        return self.coupon_template_repository.create(
            db, obj_in=coupon_template_in
        )

    def get_coupon_template(
        self, db: Session, coupon_template_id: int
    ) -> CouponTemplate | None:
        return self.coupon_template_repository.get(db, id=coupon_template_id)

    def get_all_coupon_templates(self, db: Session) -> list[CouponTemplate]:
        return self.coupon_template_repository.get_all(db)

    def update_coupon_template(
        self,
        db: Session,
        *,
        coupon_template: CouponTemplate,
        coupon_template_in: CouponTemplateUpdate,
    ) -> CouponTemplate:
        return self.coupon_template_repository.update(
            db, db_obj=coupon_template, obj_in=coupon_template_in
        )

    def remove_coupon_template(
        self, db: Session, *, coupon_template_id: int
    ) -> CouponTemplate:
        return self.coupon_template_repository.remove(db, id=coupon_template_id)
