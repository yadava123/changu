from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.models import ParcelStatus, PaymentStatus, RideStatus

class ParcelCreate(BaseModel):
    pickup_address: str = Field(min_length=3, max_length=1000); drop_address: str = Field(min_length=3, max_length=1000); sender_name: str = Field(min_length=2, max_length=120); receiver_name: str = Field(min_length=2, max_length=120); parcel_type: str = Field(min_length=2, max_length=40); weight_kg: Decimal = Field(gt=0, le=100)
class ParcelResponse(ParcelCreate):
    model_config=ConfigDict(from_attributes=True)
    id:int; customer_id:int; driver_id:int|None; price:Decimal; payment_status:PaymentStatus; status:ParcelStatus; created_at:datetime; updated_at:datetime
class RideCreate(BaseModel):
    pickup_address: str = Field(min_length=3, max_length=1000); destination: str = Field(min_length=3, max_length=1000); ride_type: str = Field(default="STANDARD", min_length=2, max_length=30)
class RideResponse(RideCreate):
    model_config=ConfigDict(from_attributes=True)
    id:int; customer_id:int; driver_id:int|None; fare:Decimal; payment_status:PaymentStatus; status:RideStatus; created_at:datetime; updated_at:datetime