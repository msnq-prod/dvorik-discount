from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.events import AuditLogRepository
from app.schemas.events import AuditLog

router = APIRouter()


def get_audit_log_repository(db: Session = Depends(get_db)) -> AuditLogRepository:
    return AuditLogRepository(db=db)


@router.get(
    "/",
    response_model=list[AuditLog],
    summary="Get all audit logs",
    description="Retrieves a list of all audit logs, with optional pagination.",
)
def read_audit_logs(
    skip: int = 0,
    limit: int = 100,
    audit_log_repo: AuditLogRepository = Depends(get_audit_log_repository),
) -> Any:
    """
    Retrieve audit logs.
    """
    return audit_log_repo.get_multi(skip=skip, limit=limit)
