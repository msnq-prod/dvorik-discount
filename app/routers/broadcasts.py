from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_admin_with_role
from app.db import get_db
from app.models.admins import Admin
from app.models.broadcasts import Broadcast, BroadcastStatus
from app.schemas.broadcasts import BroadcastCreate, BroadcastSchema
from app.tasks.broadcasts import send_broadcast

router = APIRouter(prefix="/api/v1/broadcasts", tags=["Broadcasts"])


@router.post("/")
async def create_broadcast(
    payload: BroadcastCreate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_admin_with_role("marketing")),
) -> dict[str, Any]:
    broadcast = Broadcast(
        title=payload.title,
        body=payload.body,
        media_type=payload.media_type,
        media_payload=payload.media_payload,
        status=BroadcastStatus.scheduled,
        is_test=payload.is_test,
        scheduled_at=payload.scheduled_at,
    )
    db.add(broadcast)
    db.commit()
    db.refresh(broadcast)

    return BroadcastSchema.model_validate(broadcast).model_dump()
