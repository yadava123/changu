from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FoodItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int
    name: str
    description: str
    price: Decimal
    category: str
    image_url: str | None
    is_available: bool
    created_at: datetime
    updated_at: datetime
