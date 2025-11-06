from app.db.models.loyalty import Client, Level
from app.db.repositories.base import BaseRepository
from app.schemas.loyalty import ClientCreate, ClientUpdate, LevelCreate, LevelUpdate


class ClientRepository(BaseRepository[Client, ClientCreate, ClientUpdate]):
    def __init__(self):
        super().__init__(Client)

    def get_by_identifier(self, db, *, identifier: str) -> Client | None:
        return db.query(self.model).filter(self.model.identifier == identifier).first()


class LevelRepository(BaseRepository[Level, LevelCreate, LevelUpdate]):
    def __init__(self):
        super().__init__(Level)
