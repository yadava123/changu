from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=1, max_length=1000)

class ReviewResponse(ReviewCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    order_id: int
    created_at: datetime
    updated_at: datetime