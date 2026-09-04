from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class VendorProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=2, max_length=2000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: str = Field(min_length=2, max_length=80)
    image_url: str | None = None
    stock_quantity: int = Field(ge=0)
    is_available: bool = True


class VendorProductResponse(VendorProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    seller_id: int
    created_at: datetime
    updated_at: datetime


class VendorFoodCreate(VendorProductCreate):
    pass


class VendorFoodResponse(VendorProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime
