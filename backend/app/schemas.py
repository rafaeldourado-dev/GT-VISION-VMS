from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from .models import UserRole, ClientStatus

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserSchema(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: UserRole
    api_key: Optional[str] = None
    class Config:
        from_attributes = True

class CameraBase(BaseModel):
    name: str
    rtsp_url: str

class CameraCreate(CameraBase):
    pass

class CameraSchema(CameraBase):
    id: int
    owner_id: int
    ai_enabled: bool
    class Config:
        from_attributes = True

class VehicleSightingCreate(BaseModel):
    license_plate: str
    confidence: float
    camera_id: int
    vehicle_type: Optional[str] = None
    vehicle_color: Optional[str] = None

class VehicleSightingSchema(VehicleSightingCreate):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

# --- Novas schemas para o CRM ---
class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    status: ClientStatus = ClientStatus.LEAD
    value: float = 0.0
    source: Optional[str] = None
    assigned_to: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientSchema(ClientBase):
    id: int
    last_contact: datetime
    class Config:
        from_attributes = True