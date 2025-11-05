from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_admin_with_role
from app.db import get_db
from app.models.admins import Admin
from app.models.cashiers import Cashier
from app.models.logs_and_orders import AuditLog
from app.schemas.cashiers import CashierSchema

router = APIRouter(prefix="/api/v1/cashiers", tags=["Cashiers"])


@router.get("/requests")
async def list_pending_cashiers(
    db: Session = Depends(get_db),
    _: Admin = Depends(get_admin_with_role("marketing")),
) -> list[dict[str, Any]]:
    stmt = select(Cashier).where(Cashier.is_active.is_(False))
    cashiers = (await db.execute(stmt)).scalars().all()
    return [CashierSchema.model_validate(cashier).model_dump() for cashier in cashiers]


async def _toggle_cashier(
    cashier_id: int,
    *,
    activate: bool,
    db: Session,
    admin: Admin,
) -> dict[str, Any]:
    cashier = await db.get(Cashier, cashier_id)
    if cashier is None:
        raise HTTPException(status_code=404, detail="Cashier not found")

    if cashier.is_active == activate:
        return CashierSchema.model_validate(cashier).model_dump()

    cashier.is_active = activate
    linked_admin = (await db.execute(select(Admin).where(Admin.telegram_id == cashier.telegram_id))).scalars().first()
    if linked_admin is not None:
        linked_admin.is_active = activate
        db.add(linked_admin)
    log_action = "approve_cashier" if activate else "deactivate_cashier"
    audit_log = AuditLog(
        admin_id=admin.id,
        action=log_action,
        payload={"cashier_id": cashier.id},
    )
    db.add(cashier)
    db.add(audit_log)
    await db.commit()
    await db.refresh(cashier)

    return CashierSchema.model_validate(cashier).model_dump()


@router.post("/{cashier_id}/activate")
async def activate_cashier(
    cashier_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_with_role("owner")),
) -> dict[str, Any]:
    return await _toggle_cashier(cashier_id, activate=True, db=db, admin=admin)


@router.post("/{cashier_id}/deactivate")
async def deactivate_cashier(
    cashier_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_with_role("owner")),
) -> dict[str, Any]:
    return await _toggle_cashier(cashier_id, activate=False, db=db, admin=admin)
