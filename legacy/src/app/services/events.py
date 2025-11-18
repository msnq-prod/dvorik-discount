from sqlalchemy.orm import Session

from app.db.repositories.events import AuditLogRepository, EventRepository
from app.schemas.events import AuditLogCreate, EventCreate


class AuditService:
    def __init__(self, audit_log_repository: AuditLogRepository):
        self.audit_log_repository = audit_log_repository

    def log_action(self, db: Session, *, log_in: AuditLogCreate):
        self.audit_log_repository.create(db, obj_in=log_in)


class EventService:
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository

    def record_event(self, db: Session, *, event_in: EventCreate):
        self.event_repository.create(db, obj_in=event_in)
