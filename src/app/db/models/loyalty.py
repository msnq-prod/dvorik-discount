from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.schemas.enums import GenderEnum


class Level(Base):
    """Model for loyalty levels."""

    __tablename__ = "levels"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    threshold_amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    perks: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    order: Mapped[int] = mapped_column(
        Integer, nullable=False, unique=True, name='"order"'
    )

    __table_args__ = (
        CheckConstraint("threshold_amount >= 0", name="levels_threshold_amount_check"),
    )


class Client(Base):
    """Model for clients."""

    __tablename__ = "clients"

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=True)
    gender: Mapped[GenderEnum] = mapped_column(
        Enum(GenderEnum, name="gender_enum", create_type=False),
        nullable=False,
        server_default=GenderEnum.unknown.name,
    )
    identifier: Mapped[str] = mapped_column(Text, unique=True, nullable=True)
    level_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("levels.id", ondelete="SET NULL"),
        nullable=True,
    )
    total_spent: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0"
    )
    tags: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    is_subscribed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    consents: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )

    level: Mapped["Level"] = relationship(backref="clients")

    __table_args__ = (
        CheckConstraint(
            "identifier IS NULL OR identifier ~ '^[А-ЯЁ]{2}-[0-9]{3}$'",
            name="clients_identifier_format_chk",
        ),
        CheckConstraint("total_spent >= 0", name="clients_total_spent_check"),
    )
