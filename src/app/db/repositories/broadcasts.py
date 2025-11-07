from app.db.models.events import Broadcast
from app.db.repositories.base import BaseRepository
from app.schemas.broadcasts import BroadcastCreate, BroadcastUpdate


class BroadcastRepository(BaseRepository[Broadcast, BroadcastCreate, BroadcastUpdate]):
    def __init__(self):
        super().__init__(Broadcast)
