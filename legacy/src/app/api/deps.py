from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import SessionLocal
from app.services.events import AuditService
from app.db.repositories.events import AuditLogRepository


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.db.repositories.events import EventRepository
from app.services.events import EventService


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    audit_log_repository = AuditLogRepository()
    return AuditService(audit_log_repository)


def get_event_service(db: Session = Depends(get_db)) -> EventService:
    event_repository = EventRepository()
    return EventService(event_repository)
