from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BusinessType(str, Enum):
    RESTAURANT = "RESTAURANT"
    HOME_CHEF = "HOME_CHEF"
    GROCERY = "GROCERY"
    FRESH_MEAT = "FRESH_MEAT"
    BAKERY = "BAKERY"
    ARTISAN = "ARTISAN"
    MSME = "MSME"
    LOCAL_SELLER = "LOCAL_SELLER"
    OTHER = "OTHER"


class ApplicationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class VendorApplication(Base):
    __tablename__ = "vendor_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    business_name: Mapped[str] = mapped_column(String(160), nullable=False)
    business_type: Mapped[BusinessType] = mapped_column(SqlEnum(BusinessType, name="business_type", native_enum=False), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    area: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    pincode: Mapped[str] = mapped_column(String(6), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(SqlEnum(ApplicationStatus, name="application_status", native_enum=False), default=ApplicationStatus.PENDING, nullable=False)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")
