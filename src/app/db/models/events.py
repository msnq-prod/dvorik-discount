from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    Text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.schemas.enums import (
    ActorTypeEnum,
    BroadcastStatusEnum,
    CampaignEventTypeEnum,
    SubscriptionStatusEnum,
)


class CampaignEvent(Base):
    """Model for campaign events."""

    __tablename__ = "campaign_events"

    ts: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    type: Mapped[CampaignEventTypeEnum] = mapped_column(
        Enum(CampaignEventTypeEnum, name="campaign_event_type_enum", create_type=False),
        nullable=False,
    )
    campaign_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    coupon_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    campaign: Mapped["Campaign"] = relationship(backref="events")
    client: Mapped["Client"] = relationship(backref="campaign_events")
    coupon: Mapped["Coupon"] = relationship(backref="campaign_events")

    __table_args__ = (
        CheckConstraint("amount IS NULL OR amount >= 0", name="campaign_events_amount_check"),
    )


class Broadcast(Base):
    """Model for broadcasts."""

    __tablename__ = "broadcasts"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    audience_filter: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    content: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    schedule_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[BroadcastStatusEnum] = mapped_column(
        Enum(BroadcastStatusEnum, name="broadcast_status_enum", create_type=False),
        nullable=False,
        server_default=BroadcastStatusEnum.draft.name,
    )
    sent_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")


class Subscription(Base):
    """Model for client subscriptions to channels."""

    __tablename__ = "subscriptions"

    client_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    channel_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SubscriptionStatusEnum] = mapped_column(
        Enum(SubscriptionStatusEnum, name="subscription_status_enum", create_type=False),
        nullable=False,
        server_default=SubscriptionStatusEnum.unknown.name,
    )
    checked_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    client: Mapped["Client"] = relationship(backref="subscriptions")


class AuditLog(Base):
    """Model for audit logs."""

    __tablename__ = "audit_log"

    ts: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    actor_type: Mapped[ActorTypeEnum] = mapped_column(
        Enum(ActorTypeEnum, name="actor_type_enum", create_type=False), nullable=False
    )
    actor_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(Text, nullable=True)
    entity_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    ip: Mapped[str] = mapped_column(INET, nullable=True)


class Event(Base):
    """Model for unified event log."""

    __tablename__ = "events"

    ts: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    actor_type: Mapped[ActorTypeEnum] = mapped_column(
        Enum(ActorTypeEnum, name="actor_type_enum", create_type=False), nullable=True
    )
    actor_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    entity_type: Mapped[str] = mapped_column(Text, nullable=True)
    entity_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
