from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.order import OrderStatus, PaymentMethod, PaymentStatus
from app.schemas.driver import DeliveryResponse


class AddressRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=15)
    address_line: str = Field(min_length=3, max_length=255)
    area: str = Field(min_length=2, max_length=120)
    city: str = Field(min_length=2, max_length=80)
    state: str = Field(min_length=2, max_length=80)
    pincode: str = Field(pattern=r"^\d{6}$")
    latitude: float | None = None
    longitude: float | None = None
    is_default: bool = False

    @field_validator("phone")
    @classmethod
    def phone_digits(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Phone must contain only digits")
        return value


class AddressResponse(AddressRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class CartItemRequest(BaseModel):
    food_item_id: int | None = Field(default=None, gt=0)
    product_id: int | None = Field(default=None, gt=0)
    quantity: int = Field(gt=0, le=99)

    def model_post_init(self, __context):
        if (self.food_item_id is None) == (self.product_id is None):
            raise ValueError("Provide exactly one food_item_id or product_id")


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0, le=99)


class CartItemResponse(BaseModel):
    id: int
    name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    image_url: str | None
    type: str
    food_item_id: int | None
    product_id: int | None


class CartResponse(BaseModel):
    cart_id: int | None
    items: list[CartItemResponse]
    subtotal: Decimal
    delivery_fee: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal


class OrderCreateRequest(BaseModel):
    address_id: int = Field(gt=0)
    payment_method: PaymentMethod
    coupon_code: str | None = Field(default=None, min_length=3, max_length=40)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    item_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    food_item_id: int | None
    product_id: int | None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_number: str
    status: OrderStatus
    subtotal: Decimal
    delivery_fee: Decimal
    tax: Decimal
    discount: Decimal
    total_amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    delivery_address: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]
    delivery: DeliveryResponse | None = None
