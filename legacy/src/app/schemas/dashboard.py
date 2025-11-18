from app.schemas.base import BaseSchema


class DashboardData(BaseSchema):
    issued_coupons: int
    redeemed_coupons: int
    purchases: int
    revenue: float
