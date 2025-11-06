from sqlalchemy.orm import Session

from app.db.models.loyalty import Client
from app.db.repositories.loyalty import LevelRepository


class LoyaltyService:
    def __init__(self, level_repository: LevelRepository):
        self.level_repository = level_repository

    def recalculate_level(self, db: Session, *, client: Client) -> Client:
        levels = self.level_repository.get_all(db)
        new_level = None
        for level in sorted(levels, key=lambda x: x.threshold_amount, reverse=True):
            if client.total_spent >= level.threshold_amount:
                new_level = level
                break

        if new_level and client.level_id != new_level.id:
            client.level_id = new_level.id
            db.add(client)
            db.commit()
            db.refresh(client)

        return client
