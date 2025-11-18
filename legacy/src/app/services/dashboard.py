from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.promotions import Coupon
from app.schemas.enums import CouponStatusEnum
from app.schemas.dashboard import DashboardData


class DashboardService:
    def get_dashboard_data(
        self,
        db: Session,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> DashboardData:
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = date.today()

        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)

        issued_coupons = db.scalar(
            select(func.count(Coupon.id)).where(
                Coupon.status == CouponStatusEnum.issued,
                Coupon.issued_at.between(start_dt, end_dt),
            )
        )
        redeemed_coupons = db.scalar(
            select(func.count(Coupon.id)).where(
                Coupon.status == CouponStatusEnum.redeemed,
                Coupon.redeemed_at.between(start_dt, end_dt),
            )
        )
        purchases = redeemed_coupons  # For MVP, purchases are only tracked via coupons
        revenue = db.scalar(
            select(func.sum(Coupon.redemption_amount)).where(
                Coupon.status == CouponStatusEnum.redeemed,
                Coupon.redeemed_at.between(start_dt, end_dt),
            )
        )

        return DashboardData(
            issued_coupons=issued_coupons or 0,
            redeemed_coupons=redeemed_coupons or 0,
            purchases=purchases or 0,
            revenue=revenue or 0.0,
        )
