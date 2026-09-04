from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    owner_id: int
    phone: str
    address: str
    city: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
