from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.order import PaymentStatus

class ParcelStatus(str, Enum):
    PENDING="PENDING"; ACCEPTED="ACCEPTED"; PICKED_UP="PICKED_UP"; IN_TRANSIT="IN_TRANSIT"; OUT_FOR_DELIVERY="OUT_FOR_DELIVERY"; DELIVERED="DELIVERED"; CANCELLED="CANCELLED"
class RideStatus(str, Enum):
    REQUESTED="REQUESTED"; DRIVER_ASSIGNED="DRIVER_ASSIGNED"; DRIVER_ARRIVING="DRIVER_ARRIVING"; DRIVER_ARRIVED="DRIVER_ARRIVED"; RIDE_STARTED="RIDE_STARTED"; RIDE_COMPLETED="RIDE_COMPLETED"; CANCELLED="CANCELLED"

class Parcel(Base):
    __tablename__ = "parcels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"), index=True)
    pickup_address: Mapped[str] = mapped_column(Text, nullable=False)
    drop_address: Mapped[str] = mapped_column(Text, nullable=False)
    sender_name: Mapped[str] = mapped_column(String(120), nullable=False)
    receiver_name: Mapped[str] = mapped_column(String(120), nullable=False)
    parcel_type: Mapped[str] = mapped_column(String(40), nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(SqlEnum(PaymentStatus, name="parcel_payment_status", native_enum=False), default=PaymentStatus.PENDING, nullable=False)
    status: Mapped[ParcelStatus] = mapped_column(SqlEnum(ParcelStatus, name="parcel_status", native_enum=False), default=ParcelStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Ride(Base):
    __tablename__ = "rides"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"), index=True)
    pickup_address: Mapped[str] = mapped_column(Text, nullable=False)
    destination: Mapped[str] = mapped_column(Text, nullable=False)
    ride_type: Mapped[str] = mapped_column(String(30), nullable=False)
    fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(SqlEnum(PaymentStatus, name="ride_payment_status", native_enum=False), default=PaymentStatus.PENDING, nullable=False)
    status: Mapped[RideStatus] = mapped_column(SqlEnum(RideStatus, name="ride_status", native_enum=False), default=RideStatus.REQUESTED, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)