from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.emergency_provider import ProviderType
from app.models.emergency_request import EmergencyPriority, EmergencyStatus, EmergencyType
from app.models.vendor_application import ApplicationStatus

class ProviderApplicationRequest(BaseModel):
    provider_type: ProviderType; business_name: str=Field(min_length=2); contact_name: str=Field(min_length=2); phone: str=Field(min_length=10,max_length=15); email: EmailStr; address: str=Field(min_length=3); area: str=Field(min_length=2); city: str=Field(min_length=2); state: str=Field(min_length=2); pincode: str=Field(pattern=r"^\d{6}$")
    @field_validator("phone")
    @classmethod
    def digits(cls,v):
        if not v.isdigit(): raise ValueError("Phone must contain only digits")
        return v
class ProviderApplicationResponse(ProviderApplicationRequest):
    model_config=ConfigDict(from_attributes=True)
    id:int; user_id:int; status:ApplicationStatus; admin_notes:str|None; created_at:datetime; updated_at:datetime
class EmergencyRequestCreate(BaseModel):
    emergency_type: EmergencyType; description: str=Field(min_length=3); priority: EmergencyPriority; phone: str=Field(min_length=10,max_length=15); address: str=Field(min_length=3); area: str=Field(min_length=2); city: str=Field(min_length=2); state: str=Field(min_length=2); pincode: str=Field(pattern=r"^\d{6}$"); latitude: float|None=None; longitude: float|None=None
class EmergencyRequestResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; request_number:str; user_id:int; emergency_type:EmergencyType; description:str; phone:str; address:str; area:str; city:str; state:str; pincode:str; status:EmergencyStatus; priority:EmergencyPriority; provider_id:int|None; accepted_at:datetime|None; assigned_at:datetime|None; on_the_way_at:datetime|None; arrived_at:datetime|None; resolved_at:datetime|None; cancelled_at:datetime|None; created_at:datetime; updated_at:datetime
class ProviderStatusRequest(BaseModel): is_online: bool
