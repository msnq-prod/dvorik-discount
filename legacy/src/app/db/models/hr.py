from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.schemas.enums import EmployeeRoleEnum, ShiftStatusEnum


class Employee(Base):
    """Model for employees."""

    __tablename__ = "employees"

    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    role: Mapped[EmployeeRoleEnum] = mapped_column(
        Enum(EmployeeRoleEnum, name="employee_role_enum", create_type=False),
        nullable=False,
        server_default=EmployeeRoleEnum.cashier.name,
    )
    hourly_rate: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="0"
    )
    permissions: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    __table_args__ = (
        CheckConstraint("hourly_rate >= 0", name="employees_hourly_rate_check"),
    )


class Shift(Base):
    """Model for employee shifts."""

    __tablename__ = "shifts"

    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    hours: Mapped[float] = mapped_column(
        Numeric(4, 2), nullable=False, server_default="8.00"
    )
    status: Mapped[ShiftStatusEnum] = mapped_column(
        Enum(ShiftStatusEnum, name="shift_status_enum", create_type=False),
        nullable=False,
        server_default=ShiftStatusEnum.planned.name,
    )

    employee: Mapped["Employee"] = relationship(backref="shifts")

    __table_args__ = (
        UniqueConstraint("employee_id", "date", name="shifts_employee_id_date_uc"),
        CheckConstraint("hours >= 0", name="shifts_hours_check"),
    )


class Payroll(Base):
    """Model for employee payroll."""

    __tablename__ = "payroll"

    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    month: Mapped[Date] = mapped_column(Date, nullable=False)
    shifts_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    gross: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0"
    )
    taxes: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0"
    )
    net: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0"
    )

    employee: Mapped["Employee"] = relationship(backref="payrolls")

    __table_args__ = (
        UniqueConstraint("employee_id", "month", name="payroll_employee_id_month_uc"),
        CheckConstraint("shifts_count >= 0", name="payroll_shifts_count_check"),
        CheckConstraint("gross >= 0", name="payroll_gross_check"),
        CheckConstraint("taxes >= 0", name="payroll_taxes_check"),
        CheckConstraint("net >= 0", name="payroll_net_check"),
    )
