from app.db.models.loyalty import Client, Level
from app.db.repositories.base import BaseRepository
from app.schemas.loyalty import ClientCreate, ClientUpdate, LevelCreate, LevelUpdate


class ClientRepository(BaseRepository[Client, ClientCreate, ClientUpdate]):
    def __init__(self):
        super().__init__(Client)

    def get_by_identifier(self, db, *, identifier: str) -> Client | None:
        return db.query(self.model).filter(self.model.identifier == identifier).first()

    def get_by_tg_id(self, db, *, tg_id: int) -> Client | None:
        return db.query(self.model).filter(self.model.tg_id == tg_id).first()


class LevelRepository(BaseRepository[Level, LevelCreate, LevelUpdate]):
    def __init__(self):
        super().__init__(Level)
