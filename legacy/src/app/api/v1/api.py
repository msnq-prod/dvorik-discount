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
    purchases,
    broadcasts,
    shifts,
    payrolls,
    audit_logs,
    events,
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
api_router.include_router(purchases.router, prefix="/purchases", tags=["purchases"])
api_router.include_router(broadcasts.router, prefix="/broadcasts", tags=["broadcasts"])
api_router.include_router(shifts.router, prefix="/shifts", tags=["shifts"])
api_router.include_router(payrolls.router, prefix="/payrolls", tags=["payrolls"])
api_router.include_router(
    audit_logs.router, prefix="/audit-logs", tags=["audit-logs"]
)
api_router.include_router(events.router, prefix="/events", tags=["events"])
