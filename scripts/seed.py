import os

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.db.models.loyalty import Level
from app.db.models.hr import Employee
from app.schemas.enums import EmployeeRoleEnum

load_dotenv()

def seed_data():
    """Seeds the database with initial data."""
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable is not set.")

    engine = create_engine(db_url, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as session:
        # Seed default loyalty level
        if not session.execute(select(Level).where(Level.name == "Bronze")).scalar_one_or_none():
            default_level = Level(
                name="Bronze",
                threshold_amount=0,
                perks={"discount": 0},
                order=1,
            )
            session.add(default_level)

        # Seed admin user
        admin_tg_id = os.getenv("FIRST_SUPERADMIN_TG_ID")
        if admin_tg_id and not session.execute(select(Employee).where(Employee.tg_id == admin_tg_id)).scalar_one_or_none():
            admin_user = Employee(
                full_name="Admin",
                tg_id=admin_tg_id,
                role=EmployeeRoleEnum.owner,
                hourly_rate=0,
                active=True,
            )
            session.add(admin_user)

        session.commit()

if __name__ == "__main__":
    seed_data()
