from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.vendor_application import ApplicationStatus, BusinessType


class VendorApplicationRequest(BaseModel):
    business_name: str = Field(min_length=2, max_length=160)
    business_type: BusinessType
    description: str = Field(min_length=2, max_length=2000)
    phone: str = Field(min_length=10, max_length=15)
    email: EmailStr
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


class VendorApplicationResponse(VendorApplicationRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: ApplicationStatus
    admin_notes: str | None
    created_at: datetime
    updated_at: datetime


class VendorResponse(VendorApplicationRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    logo_url: str | None
    cover_image_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class VendorStoreUpdate(BaseModel):
    business_name: str = Field(min_length=2, max_length=160)
    business_type: BusinessType = BusinessType.OTHER
    description: str = Field(min_length=2, max_length=2000)
    phone: str = Field(min_length=10, max_length=15)
    email: EmailStr
    address: str = Field(min_length=3, max_length=255)
    area: str = Field(min_length=2, max_length=120)
    city: str = Field(min_length=2, max_length=80)
    state: str = Field(min_length=2, max_length=80)
    pincode: str = Field(pattern=r"^\d{6}$")
    logo_url: str | None = None
    cover_image_url: str | None = None
    is_active: bool = True


class AdminApplicationDecision(BaseModel):
    status: ApplicationStatus
    admin_notes: str | None = Field(default=None, max_length=2000)
