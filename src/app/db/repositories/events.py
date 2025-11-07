from app.db.models.events import Broadcast, AuditLog, Event
from app.db.repositories.base import BaseRepository
from app.schemas.broadcasts import BroadcastCreate, BroadcastUpdate
from app.schemas.events import AuditLogCreate, EventCreate


class BroadcastRepository(BaseRepository[Broadcast, BroadcastCreate, BroadcastUpdate]):
    def __init__(self):
        super().__init__(Broadcast)


class AuditLogRepository(BaseRepository[AuditLog, AuditLogCreate, AuditLogCreate]):
    def __init__(self):
        super().__init__(AuditLog)


class EventRepository(BaseRepository[Event, EventCreate, EventCreate]):
    def __init__(self):
        super().__init__(Event)
