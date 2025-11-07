from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.schemas.enums import CampaignStatusEnum, CouponStatusEnum, DiscountTypeEnum


class Campaign(Base):
    """Model for campaigns."""

    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    start_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    channels: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    ref_code: Mapped[str] = mapped_column(Text, unique=True, nullable=True)
    ref_url: Mapped[str] = mapped_column(Text, unique=True, nullable=True)
    template_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("coupon_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[CampaignStatusEnum] = mapped_column(
        Enum(CampaignStatusEnum, name="campaign_status_enum", create_type=False),
        nullable=False,
        server_default=CampaignStatusEnum.draft.name,
    )
    utm: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    attribution_window_days: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="7"
    )
    code_prefix: Mapped[str] = mapped_column(Text, nullable=True)

    template: Mapped["CouponTemplate"] = relationship(backref="campaigns")

    __table_args__ = (
        CheckConstraint(
            "attribution_window_days BETWEEN 1 AND 90",
            name="campaigns_attribution_window_days_check",
        ),
    )


class CouponTemplate(Base):
    """Model for coupon templates."""

    __tablename__ = "coupon_templates"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    code_pattern: Mapped[str] = mapped_column(Text, nullable=False)
    discount_type: Mapped[DiscountTypeEnum] = mapped_column(
        Enum(DiscountTypeEnum, name="discount_type_enum", create_type=False),
        nullable=False,
    )
    discount_value: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0"
    )
    min_purchase: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    per_user_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    usage_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    expiration_days: Mapped[int] = mapped_column(Integer, nullable=True)
    stacking_rules: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    __table_args__ = (
        CheckConstraint("discount_value >= 0", name="coupon_templates_discount_value_check"),
        CheckConstraint(
            "min_purchase IS NULL OR min_purchase >= 0",
            name="coupon_templates_min_purchase_check",
        ),
        CheckConstraint(
            "per_user_limit IS NULL OR per_user_limit >= 0",
            name="coupon_templates_per_user_limit_check",
        ),
        CheckConstraint(
            "usage_limit IS NULL OR usage_limit >= 0",
            name="coupon_templates_usage_limit_check",
        ),
        CheckConstraint(
            "expiration_days IS NULL OR expiration_days >= 0",
            name="coupon_templates_expiration_days_check",
        ),
    )


class Coupon(Base):
    """Model for coupons."""

    __tablename__ = "coupons"

    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    template_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("coupon_templates.id", ondelete="RESTRICT"),
        nullable=False,
    )
    client_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    campaign_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[CouponStatusEnum] = mapped_column(
        Enum(CouponStatusEnum, name="coupon_status_enum", create_type=False),
        nullable=False,
        server_default=CouponStatusEnum.draft.name,
    )
    issued_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    redeemed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    redeemed_by_employee_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    redemption_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    fraud_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    template: Mapped["CouponTemplate"] = relationship(backref="coupons")
    client: Mapped["Client"] = relationship(backref="coupons")
    campaign: Mapped["Campaign"] = relationship(backref="coupons")

    __table_args__ = (
        CheckConstraint("code ~ '^[А-ЯЁ]{2}-[0-9]{5}$'", name="coupons_code_format_chk"),
        CheckConstraint(
            "(status != 'redeemed') OR (redeemed_at IS NOT NULL)",
            name="coupons_redeemed_chk",
        ),
        CheckConstraint(
            "redemption_amount IS NULL OR redemption_amount >= 0",
            name="coupons_redemption_amount_check",
        ),
    )
