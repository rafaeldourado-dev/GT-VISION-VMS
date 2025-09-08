from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .models import UserRole

# Schema para a câmera dentro da resposta de avistamento
class CameraInSighting(BaseModel):
    name: str

# Schemas de Veículos (Sighting)
class VehicleSightingBase(BaseModel):
    license_plate: str
    image_filename: str
    camera_id: int

class VehicleSightingCreate(VehicleSightingBase):
    pass

class VehicleSighting(VehicleSightingBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

# --- NOVO SCHEMA PARA A RESPOSTA DO FRONTEND ---
class VehicleSightingResponse(BaseModel):
    id: int
    plate: str
    camera: CameraInSighting
    timestamp: datetime

# Schemas de Câmera
class CameraBase(BaseModel):
    name: str
    rtsp_url: str
    is_active: bool = True

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    is_active: Optional[bool] = None

class Camera(CameraBase):
    id: int
    client_id: int
    class Config:
        from_attributes = True

# Schemas de Usuário
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    client_id: int
    role: UserRole = UserRole.CLIENT_USER

class User(UserBase):
    id: int
    is_active: bool
    client_id: int
    role: UserRole
    class Config:
        from_attributes = True

# Schemas de Cliente
class ClientBase(BaseModel):
    name: str

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

# Schemas de Lead (CRM)
class LeadBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# Schemas de Autenticação
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Schemas de Dashboard
class DashboardStats(BaseModel):
    total_cameras: int
    online_cameras: int
    sightings_today: int
    alerts_24h: int