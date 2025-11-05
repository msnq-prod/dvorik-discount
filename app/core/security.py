from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.admins import Admin, AdminRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login-token")


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        raise credentials_exception from exc

    subject = payload.get("sub")
    if subject is None:
        raise credentials_exception

    try:
        admin_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise credentials_exception from exc

    admin = db.get(Admin, admin_id)
    if admin is None:
        raise credentials_exception
    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin is inactive")

    return admin


def get_admin_with_role(required_role: str) -> Callable[[Admin], Admin]:
    try:
        role_enum = AdminRole(required_role)
    except ValueError as exc:
        raise ValueError(f"Unknown admin role: {required_role}") from exc

    def _enforce_role(admin: Admin = Depends(get_current_admin)) -> Admin:
        if admin.role not in {AdminRole.owner, role_enum}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return admin

    return _enforce_role
