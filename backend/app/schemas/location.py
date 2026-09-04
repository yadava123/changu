from datetime import datetime

from pydantic import BaseModel, Field


class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class LocationResponse(LocationUpdate):
    updated_at: datetime | None = None