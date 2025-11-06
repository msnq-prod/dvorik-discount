from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.dashboard import DashboardData
from app.services.dashboard import DashboardService

router = APIRouter()


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService()


@router.get("/", response_model=DashboardData)
def read_dashboard_data(
    *,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    db: Session = Depends(get_db),
):
    return dashboard_service.get_dashboard_data(
        db, start_date=start_date, end_date=end_date
    )
