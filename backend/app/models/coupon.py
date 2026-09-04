from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Coupon(Base):
    __tablename__ = "coupons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    discount_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    discount_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    minimum_order_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    maximum_discount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    usage_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_user_limit: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class CouponUsage(Base):
    __tablename__ = "coupon_usages"
    __table_args__ = (UniqueConstraint("coupon_id", "user_id", "order_id", name="uq_coupon_usage_order"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)