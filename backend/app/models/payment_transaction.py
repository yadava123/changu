from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class PaymentTransactionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class PaymentServiceType(str, Enum):
    ORDER = "ORDER"
    PARCEL = "PARCEL"
    RIDE = "RIDE"

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True, index=True)
    service_type: Mapped[PaymentServiceType] = mapped_column(SqlEnum(PaymentServiceType, name="payment_service_type", native_enum=False), default=PaymentServiceType.ORDER, nullable=False)
    service_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[PaymentTransactionStatus] = mapped_column(SqlEnum(PaymentTransactionStatus, name="payment_transaction_status", native_enum=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)