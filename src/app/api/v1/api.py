from fastapi import APIRouter

from app.api.v1.endpoints import (
    campaigns,
    coupons,
    webhooks,
    clients,
    employees,
    coupon_templates,
    levels,
    dashboard,
)

api_router = APIRouter()
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(coupons.router, prefix="/coupons", tags=["coupons"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(
    coupon_templates.router, prefix="/coupon-templates", tags=["coupon-templates"]
)
api_router.include_router(levels.router, prefix="/levels", tags=["levels"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
