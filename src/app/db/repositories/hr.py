from app.db.models.hr import Employee
from app.db.repositories.base import BaseRepository
from app.schemas.hr import EmployeeCreate, EmployeeUpdate


class EmployeeRepository(BaseRepository[Employee, EmployeeCreate, EmployeeUpdate]):
    def __init__(self):
        super().__init__(Employee)

    def get_by_tg_id(self, db, *, tg_id: int) -> Employee | None:
        return db.query(self.model).filter(self.model.tg_id == tg_id).first()
