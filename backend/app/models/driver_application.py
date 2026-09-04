from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VehicleType(str, Enum):
    BIKE = "BIKE"
    SCOOTER = "SCOOTER"
    AUTO = "AUTO"
    CAR = "CAR"
    OTHER = "OTHER"


class DriverApplicationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DriverApplication(Base):
    __tablename__ = "driver_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    vehicle_type: Mapped[VehicleType] = mapped_column(SqlEnum(VehicleType, name="vehicle_type", native_enum=False), nullable=False)
    vehicle_number: Mapped[str] = mapped_column(String(30), nullable=False)
    license_number: Mapped[str] = mapped_column(String(40), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    area: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    pincode: Mapped[str] = mapped_column(String(6), nullable=False)
    status: Mapped[DriverApplicationStatus] = mapped_column(SqlEnum(DriverApplicationStatus, name="driver_application_status", native_enum=False), default=DriverApplicationStatus.PENDING, nullable=False)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")
