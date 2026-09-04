from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    DRIVER_ASSIGNED = "DRIVER_ASSIGNED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY"
    UPI_MANUAL = "UPI_MANUAL"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    restaurant_id: Mapped[int | None] = mapped_column(ForeignKey("restaurants.id"), nullable=True)
    seller_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(SqlEnum(OrderStatus, name="order_status", native_enum=False), default=OrderStatus.PENDING, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(SqlEnum(PaymentMethod, name="payment_method", native_enum=False), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(SqlEnum(PaymentStatus, name="payment_status", native_enum=False), default=PaymentStatus.PENDING, nullable=False)
    delivery_address: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    delivery = relationship("Delivery", uselist=False, back_populates="order")
    user = relationship("User", foreign_keys=[user_id])
