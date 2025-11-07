from sqlalchemy.orm import Session

from app.db.models.hr import Shift
from app.db.repositories.hr import ShiftRepository
from app.schemas.hr import ShiftCreate, ShiftUpdate


class ShiftService:
    def __init__(self, shift_repository: ShiftRepository):
        self.shift_repository = shift_repository

    def create_shift(self, db: Session, *, shift_in: ShiftCreate) -> Shift:
        return self.shift_repository.create(db, obj_in=shift_in)

    def get_shift(self, db: Session, shift_id: int) -> Shift | None:
        return self.shift_repository.get(db, id=shift_id)

    def get_all_shifts(self, db: Session) -> list[Shift]:
        return self.shift_repository.get_all(db)

    def update_shift(
        self, db: Session, *, shift: Shift, shift_in: ShiftUpdate
    ) -> Shift:
        return self.shift_repository.update(db, db_obj=shift, obj_in=shift_in)

    def remove_shift(self, db: Session, *, shift_id: int) -> Shift:
        return self.shift_repository.remove(db, id=shift_id)
