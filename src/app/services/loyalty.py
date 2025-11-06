from sqlalchemy.orm import Session

from app.db.models.loyalty import Client, Level
from app.db.repositories.loyalty import LevelRepository
from app.schemas.loyalty import LevelCreate, LevelUpdate


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

    def create_level(self, db: Session, *, level_in: LevelCreate) -> Level:
        return self.level_repository.create(db, obj_in=level_in)

    def get_level(self, db: Session, level_id: int) -> Level | None:
        return self.level_repository.get(db, id=level_id)

    def get_all_levels(self, db: Session) -> list[Level]:
        return self.level_repository.get_all(db)

    def update_level(
        self, db: Session, *, level: Level, level_in: LevelUpdate
    ) -> Level:
        return self.level_repository.update(db, db_obj=level, obj_in=level_in)

    def remove_level(self, db: Session, *, level_id: int) -> Level:
        return self.level_repository.remove(db, id=level_id)
