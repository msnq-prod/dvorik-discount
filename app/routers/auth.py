from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import create_access_token
from app.db import get_db
from app.models.admins import Admin
from app.schemas.admins import AdminSchema

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login-token")
async def login_with_token(
    payload: dict[str, Any],
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _ = payload  # placeholder until real one-time token logic appears

    stmt = select(Admin).where(Admin.telegram_id == settings.FIRST_SUPERADMIN_TG_ID)
    admin = (await db.execute(stmt)).scalars().first()
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")

    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin is inactive")

    token = create_access_token({"sub": str(admin.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "admin": AdminSchema.model_validate(admin),
    }
