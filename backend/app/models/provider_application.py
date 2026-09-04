from datetime import datetime
from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.vendor_application import ApplicationStatus
from app.models.emergency_provider import ProviderType

class ProviderApplication(Base):
    __tablename__ = "provider_applications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    provider_type: Mapped[ProviderType] = mapped_column(SqlEnum(ProviderType, name="provider_application_type", native_enum=False), nullable=False)
    business_name: Mapped[str] = mapped_column(String(160), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    area: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    pincode: Mapped[str] = mapped_column(String(6), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(SqlEnum(ApplicationStatus, name="provider_application_status", native_enum=False), default=ApplicationStatus.PENDING, nullable=False)
    admin_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    user = relationship("User")