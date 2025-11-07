from app.schemas.base import BaseSchema


class IdempotencyRequestBase(BaseSchema):
    idempotency_key: str
    response_payload: dict


class IdempotencyRequestCreate(IdempotencyRequestBase):
    pass


class IdempotencyRequest(IdempotencyRequestBase):
    pass
