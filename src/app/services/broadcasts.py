from sqlalchemy.orm import Session

from app.db.models.events import Broadcast
from app.db.repositories.broadcasts import BroadcastRepository
from app.schemas.broadcasts import BroadcastCreate, BroadcastUpdate
from app.workers.broadcast import send_broadcast


class BroadcastService:
    def __init__(self, broadcast_repository: BroadcastRepository):
        self.broadcast_repository = broadcast_repository

    def create_broadcast(
        self, db: Session, *, broadcast_in: BroadcastCreate
    ) -> Broadcast:
        broadcast = self.broadcast_repository.create(db, obj_in=broadcast_in)
        if broadcast.schedule_at:
            send_broadcast.apply_async(
                (broadcast.id,), eta=broadcast.schedule_at
            )
        return broadcast

    def get_broadcast(self, db: Session, broadcast_id: int) -> Broadcast | None:
        return self.broadcast_repository.get(db, id=broadcast_id)

    def get_all_broadcasts(self, db: Session) -> list[Broadcast]:
        return self.broadcast_repository.get_all(db)

    def update_broadcast(
        self, db: Session, *, broadcast: Broadcast, broadcast_in: BroadcastUpdate
    ) -> Broadcast:
        return self.broadcast_repository.update(
            db, db_obj=broadcast, obj_in=broadcast_in
        )

    def remove_broadcast(self, db: Session, *, broadcast_id: int) -> Broadcast:
        return self.broadcast_repository.remove(db, id=broadcast_id)
