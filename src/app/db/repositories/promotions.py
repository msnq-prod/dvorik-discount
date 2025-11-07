from sqlalchemy.orm import Session

from app.db.models.promotions import Campaign, Coupon, CouponTemplate
from app.db.repositories.base import BaseRepository
from app.schemas.promotions import (
    CampaignCreate,
    CampaignUpdate,
    CouponCreate,
    CouponUpdate,
    CouponTemplateCreate,
    CouponTemplateUpdate,
)


class CouponTemplateRepository(
    BaseRepository[CouponTemplate, CouponTemplateCreate, CouponTemplateUpdate]
):
    def __init__(self):
        super().__init__(CouponTemplate)


class CampaignRepository(BaseRepository[Campaign, CampaignCreate, CampaignUpdate]):
    def __init__(self):
        super().__init__(Campaign)


class CouponRepository(BaseRepository[Coupon, CouponCreate, CouponUpdate]):
    def __init__(self):
        super().__init__(Coupon)

    def get_by_code(self, db: Session, *, code: str) -> Coupon | None:
        return db.query(self.model).filter(self.model.code == code).first()

    def get_by_code_for_update(self, db: Session, *, code: str) -> Coupon | None:
        return (
            db.query(self.model)
            .filter(self.model.code == code)
            .with_for_update()
            .first()
        )
