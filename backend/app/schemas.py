# backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .models import UserRole, CameraType # Importar o novo Enum

# Schema para a câmera dentro da resposta de avistamento
class CameraInSighting(BaseModel):
    name: str
    class Config:
        from_attributes = True

# --- Schemas de Avistamento ---
class VehicleSightingBase(BaseModel):
    license_plate: str
    vehicle_color: Optional[str] = None
    vehicle_model: Optional[str] = None
    plate_image_url: Optional[str] = None

class VehicleSightingCreate(VehicleSightingBase):
    camera_id: Optional[int] = None

class VehicleSighting(VehicleSightingBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

class VehicleSightingResponse(BaseModel):
    id: int
    license_plate: str
    vehicle_color: Optional[str] = None
    vehicle_model: Optional[str] = None
    plate_image_url: Optional[str] = None
    camera: CameraInSighting
    timestamp: datetime
    class Config:
        from_attributes = True

# --- Schemas de Câmera ---
class CameraCreateOnvif(BaseModel):
    name: str
    ip_address: str
    port: int = 80
    username: str
    password: str
    is_active: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CameraBase(BaseModel):
    name: str
    rtsp_url: str
    # --- CAMPO ADICIONADO ---
    camera_type: CameraType = CameraType.GENERIC_RTSP
    # --------------------------
    is_active: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    # --- CAMPO ADICIONADO ---
    camera_type: Optional[CameraType] = None
    # --------------------------
    is_active: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Camera(CameraBase):
    id: int
    client_id: int
    class Config:
        from_attributes = True

# --- Schemas de Usuário ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

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

# --- Schemas de Cliente ---
class ClientBase(BaseModel):
    name: str

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

# --- Schemas de Lead (CRM) ---
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

# --- Schemas de Autenticação ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Schemas de Dashboard ---
class DashboardStats(BaseModel):
    total_cameras: int
    online_cameras: int
    sightings_today: int
    alerts_24h: int

# --- Schemas de Ticket ---
class TicketBase(BaseModel):
    subject: str
    description: str
    priority: str

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class Ticket(TicketBase):
    id: int
    owner_id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True