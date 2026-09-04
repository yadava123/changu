from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class ProviderType(str, Enum):
    MECHANIC = "MECHANIC"
    TOWING = "TOWING"
    FUEL = "FUEL"
    AMBULANCE = "AMBULANCE"
    DOCTOR = "DOCTOR"
    PHARMACY = "PHARMACY"
    BLOOD_NETWORK = "BLOOD_NETWORK"
    OTHER = "OTHER"

class EmergencyProvider(Base):
    __tablename__ = "emergency_providers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)
    provider_type: Mapped[ProviderType] = mapped_column(SqlEnum(ProviderType, name="provider_type", native_enum=False), nullable=False)
    business_name: Mapped[str] = mapped_column(String(160), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    area: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    pincode: Mapped[str] = mapped_column(String(6), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    user = relationship("User")