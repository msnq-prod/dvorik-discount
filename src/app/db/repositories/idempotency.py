from sqlalchemy.orm import Session

from app.db.models.idempotency import IdempotencyRequest
from app.db.repositories.base import BaseRepository
from app.schemas.idempotency import IdempotencyRequestCreate


class IdempotencyRequestRepository(
    BaseRepository[IdempotencyRequest, IdempotencyRequestCreate, None]
):
    def __init__(self):
        super().__init__(IdempotencyRequest)

    def get_by_key(
        self, db: Session, *, idempotency_key: str
    ) -> IdempotencyRequest | None:
        return db.query(self.model).filter(
            self.model.idempotency_key == idempotency_key
        ).first()
