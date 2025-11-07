import random
import string
from sqlalchemy.orm import Session, joinedload
from app.db.models.loyalty import Client, Level
from app.db.repositories.base import BaseRepository
from app.schemas.loyalty import ClientCreate, ClientUpdate, LevelCreate, LevelUpdate


class ClientRepository(BaseRepository[Client, ClientCreate, ClientUpdate]):
    def __init__(self):
        super().__init__(Client)

    def get_by_identifier(self, db, *, identifier: str) -> Client | None:
        return db.query(self.model).filter(self.model.identifier == identifier).first()

    def get_by_tg_id(self, db, *, tg_id: int) -> Client | None:
        return (
            db.query(self.model)
            .options(joinedload(self.model.level))
            .filter(self.model.tg_id == tg_id)
            .first()
        )

    def create(self, db: Session, *, obj_in: ClientCreate) -> Client:
        initials = (obj_in.first_name[0] + obj_in.last_name[0]).upper()
        while True:
            random_part = "".join(random.choices(string.digits, k=3))
            identifier = f"{initials}-{random_part}"
            if not self.get_by_identifier(db, identifier=identifier):
                break

        db_obj = self.model(**obj_in.model_dump(), identifier=identifier)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class LevelRepository(BaseRepository[Level, LevelCreate, LevelUpdate]):
    def __init__(self):
        super().__init__(Level)
