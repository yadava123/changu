from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EarningStatus(str, Enum):
    PENDING = "PENDING"
    AVAILABLE = "AVAILABLE"


class EarningRecord(Base):
    __tablename__ = "earning_records"
    __table_args__ = (UniqueConstraint("user_id", "source_type", "source_id", name="uq_earning_source"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[EarningStatus] = mapped_column(SqlEnum(EarningStatus, name="earning_status", native_enum=False), default=EarningStatus.AVAILABLE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_wallet_transaction_idempotency"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(120), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)