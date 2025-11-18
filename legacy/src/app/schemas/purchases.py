from pydantic import Field

from app.schemas.base import BaseSchema


class PurchaseCreate(BaseSchema):
    client_ref: str
    amount: float = Field(..., gt=0)
    employee_id: int
