from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.driver_application import DriverApplicationStatus, VehicleType
from app.models.delivery import DeliveryStatus


class DriverApplicationRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=15)
    email: EmailStr
    vehicle_type: VehicleType
    vehicle_number: str = Field(min_length=2, max_length=30)
    license_number: str = Field(min_length=2, max_length=40)
    address: str = Field(min_length=3, max_length=255)
    area: str = Field(min_length=2, max_length=120)
    city: str = Field(min_length=2, max_length=80)
    state: str = Field(min_length=2, max_length=80)
    pincode: str = Field(pattern=r"^\d{6}$")

    @field_validator("phone")
    @classmethod
    def phone_digits(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Phone must contain only digits")
        return value


class DriverApplicationResponse(DriverApplicationRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: DriverApplicationStatus
    admin_notes: str | None
    created_at: datetime
    updated_at: datetime


class DriverResponse(DriverApplicationRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    profile_image_url: str | None
    is_active: bool
    is_online: bool
    created_at: datetime
    updated_at: datetime


class DriverStatusRequest(BaseModel):
    is_online: bool


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    driver_id: int | None
    status: DeliveryStatus
    pickup_address: str
    delivery_address: str
    delivery_earning: int
    accepted_at: datetime | None
    picked_up_at: datetime | None
    out_for_delivery_at: datetime | None
    delivered_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DeliveryStatusRequest(BaseModel):
    status: DeliveryStatus
