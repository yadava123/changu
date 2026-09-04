from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    price: Decimal
    category: str
    seller_id: int
    image_url: str | None
    stock_quantity: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
