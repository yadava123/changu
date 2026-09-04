from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class LoyaltyAccount(Base):
    __tablename__ = "loyalty_accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class LoyaltyTransaction(Base):
    __tablename__ = "loyalty_transactions"
    __table_args__ = (UniqueConstraint("user_id", "event_key", name="uq_loyalty_user_event"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    event_key: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Referral(Base):
    __tablename__ = "referrals"
    __table_args__ = (UniqueConstraint("referrer_id", "referred_id", name="uq_referral_pair"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    referred_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), unique=True, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)