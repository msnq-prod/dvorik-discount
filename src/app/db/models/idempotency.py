from sqlalchemy import DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class IdempotencyRequest(Base):
    """Model for storing idempotency keys and their responses."""

    __tablename__ = "idempotency_requests"

    idempotency_key: Mapped[str] = mapped_column(Text, primary_key=True)
    response_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
