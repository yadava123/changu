from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.driver_application import VehicleType
from app.models.emergency_provider import ProviderType
from app.models.user import UserRole
from app.models.vendor_application import BusinessType


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name", "phone")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field is required")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Phone must contain only digits")
        return value


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class RoleRegisterRequest(RegisterRequest):
    business_name: str | None = Field(default=None, min_length=2, max_length=160)
    business_type: BusinessType | None = None
    description: str | None = Field(default=None, min_length=2, max_length=2000)
    address: str | None = Field(default=None, min_length=3, max_length=255)
    area: str | None = Field(default=None, min_length=2, max_length=120)
    city: str | None = Field(default=None, min_length=2, max_length=80)
    state: str | None = Field(default=None, min_length=2, max_length=80)
    pincode: str | None = Field(default=None, pattern=r"^\d{6}$")
    vehicle_type: VehicleType | None = None
    vehicle_number: str | None = Field(default=None, min_length=2, max_length=30)
    license_number: str | None = Field(default=None, min_length=2, max_length=40)
    provider_type: ProviderType | None = None
    contact_name: str | None = Field(default=None, min_length=2, max_length=120)


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=15)

    @field_validator("full_name", "phone")
    @classmethod
    def validate_profile_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field is required")
        return value

    @field_validator("phone")
    @classmethod
    def validate_profile_phone(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Phone must contain only digits")
        return value


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str
    role: UserRole
    is_active: bool


class PublicUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str
    role: UserRole


class RegisterResponse(BaseModel):
    message: str
    user: PublicUserResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: PublicUserResponse
