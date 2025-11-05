from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import get_admin_with_role
from app.db import get_db
from app.models.admins import Admin, AdminRole
from app.models.discounts import Discount
from app.models.logs_and_orders import AuditLog
from app.models.users import User, UserGender
from app.schemas.discounts import DiscountSchema
from app.schemas.users import UserSchema, UserUpdate

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


def _apply_filters(
    stmt,
    *,
    search: str | None,
    is_subscribed: bool | None,
    gender: UserGender | None,
    age_from: int | None,
    is_test: bool,
) -> Any:
    conditions: list[Any] = [User.is_test == is_test]

    if search:
        pattern = f"%{search.lower()}%"
        conditions.append(
            or_(
                func.lower(User.username).like(pattern),
                func.lower(User.first_name).like(pattern),
                func.lower(User.last_name).like(pattern),
                func.lower(User.display_name).like(pattern),
                func.lower(User.phone).like(pattern),
            )
        )

    if is_subscribed is not None:
        conditions.append(User.is_subscribed == is_subscribed)

    if gender is not None:
        conditions.append(User.gender == gender)

    if age_from is not None and age_from > 0:
        cutoff = date.today() - timedelta(days=age_from * 365)
        conditions.append(User.birthday.is_not(None))
        conditions.append(User.birthday <= cutoff)

    return stmt.where(*conditions)


@router.get("/")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    is_subscribed: bool | None = None,
    gender: UserGender | None = None,
    age_from: int | None = None,
    is_test: bool = False,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_admin_with_role("readonly")),
) -> dict[str, Any]:
    base_stmt = select(User)
    filtered_stmt = _apply_filters(
        base_stmt,
        search=search,
        is_subscribed=is_subscribed,
        gender=gender,
        age_from=age_from,
        is_test=is_test,
    )

    count_stmt = select(func.count()).select_from(filtered_stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * page_size
    items_stmt = (
        filtered_stmt.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    )
    users = (await db.execute(items_stmt)).scalars().all()

    items: list[dict[str, Any]] = []
    for user in users:
        data = UserSchema.model_validate(user).model_dump()
        if current_admin.role == AdminRole.readonly:
            data["phone"] = None
        items.append(data)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{user_id}")
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_admin_with_role("readonly")),
) -> dict[str, Any]:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = UserSchema.model_validate(user).model_dump()
    if current_admin.role == AdminRole.readonly:
        user_data["phone"] = None

    now = datetime.now(timezone.utc)
    active_stmt = select(Discount).where(
        Discount.user_id == user.id,
        Discount.used_at.is_(None),
        (Discount.expires_at.is_(None)) | (Discount.expires_at > now),
    )
    active_discounts = [
        DiscountSchema.model_validate(discount).model_dump()
        for discount in (await db.execute(active_stmt)).scalars().all()
    ]

    history_stmt = select(Discount).where(Discount.user_id == user.id).order_by(Discount.created_at.desc())
    discount_history = [
        DiscountSchema.model_validate(discount).model_dump()
        for discount in (await db.execute(history_stmt)).scalars().all()
    ]

    return {
        "user": user_data,
        "active_discounts": active_discounts,
        "discount_history": discount_history,
    }


@router.patch("/{user_id}")
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_admin_with_role("marketing")),
) -> dict[str, Any]:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return UserSchema.model_validate(user).model_dump()

    changes: dict[str, Any] = {}
    for field, value in update_data.items():
        old_value = getattr(user, field)
        if old_value != value:
            setattr(user, field, value)
            changes[field] = {"old": old_value, "new": value}

    if changes:
        audit_log = AuditLog(
            admin_id=current_admin.id,
            action="update_user",
            payload={"user_id": user.id, "changes": changes},
        )
        db.add(audit_log)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return UserSchema.model_validate(user).model_dump()
