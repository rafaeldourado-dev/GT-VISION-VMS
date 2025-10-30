# backend/app/schemas.py (CORRIGIDO E COMPLETO)

from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime
from .models import UserRole

# Schema para a câmera dentro da resposta de avistamento
class CameraInSighting(BaseModel):
    name: str
    class Config:
        from_attributes = True

# --- ALTERAÇÕES AQUI ---
class VehicleSightingBase(BaseModel):
    license_plate: str
    vehicle_color: Optional[str] = None
    vehicle_model: Optional[str] = None
    image_path: Optional[str] = None

class VehicleSightingCreate(VehicleSightingBase):
    camera_id: int

class VehicleSighting(VehicleSightingBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

# Schema para a resposta no frontend, incluindo o nome da câmara
class VehicleSightingResponse(BaseModel):
    id: int
    license_plate: str
    vehicle_color: Optional[str] = None
    vehicle_model: Optional[str] = None
    image_path: Optional[str] = None
    camera: CameraInSighting
    timestamp: datetime
    class Config:
        from_attributes = True
# -----------------------

# Schemas de Câmera
class CameraBase(BaseModel):
    name: str
    rtsp_url: str
    is_active: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    is_active: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Camera(CameraBase):
    id: int
    client_id: int
    thumbnail_url: Optional[str] = None
    class Config:
        from_attributes = True

# Schemas de Usuário
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
 
class UserCreate(UserBase):
    password: str
    client_id: int
    role: UserRole = UserRole.CLIENT_USER

    @field_validator('password')
    @classmethod
    def password_length(cls, v: str) -> str:
        # bcrypt has a maximum password length of 72 bytes.
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password must be 72 bytes or less.')
        return v

class User(UserBase):
    id: int
    is_active: bool
    client_id: int
    password_change_required: bool # NOVO
    role: UserRole
    class Config:
        from_attributes = True

# --- ADIÇÃO DA CLASSE FALTANTE ABAIXO ---
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
# ---------------------------------------

# --- CORREÇÕES E ADIÇÕES NOS SCHEMAS DE SENHA ---

# 1. Classe que faltava (causava o AttributeError)
class PasswordResetRequest(BaseModel):
    """Schema para solicitar um reset de senha"""
    email: EmailStr

# 2. Classe renomeada e corrigida (evita erro futuro)
class PasswordReset(BaseModel):
    """Schema para finalizar o reset de senha com um token"""
    token: str
    new_password: str

# 3. Classe renomeada e corrigida (evita erro futuro)
class PasswordChange(BaseModel):
    """Schema para a mudança forçada de senha"""
    old_password: str
    new_password: str
# ---------------------------------------------------------

# --- NOVO: Schema para troca de senha inicial (sem autenticação) ---
class ForcedPasswordChange(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str

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

# --- ADIÇÃO DOS SCHEMAS FALTANTES ABAIXO ---
class BlacklistedPlateBase(BaseModel):
    license_plate: str
    reason: Optional[str] = None

class BlacklistedPlateCreate(BlacklistedPlateBase):
    pass

class BlacklistedPlate(BlacklistedPlateBase):
    id: int
    client_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
# -------------------------------------------

# Schemas de Chave de API (para uso interno)
class ApiKeyBase(BaseModel):
    key: str
    name: Optional[str] = None
    is_active: bool = True

class ApiKeyCreate(ApiKeyBase):
    client_id: Optional[int] = None # Pode ser nulo para chaves globais

class ApiKey(ApiKeyBase):
    id: int
    client_id: Optional[int] = None
    created_at: datetime
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

# --- ADIÇÕES PARA CORRIGIR O ERRO ---
# Classes que estavam faltando e causando o AttributeError em users.py

class UserSelfPasswordUpdate(BaseModel):
    """Schema para o próprio usuário alterar a senha."""
    current_password: str
    new_password: str

class UserPasswordReset(BaseModel):
    """Schema para o admin resetar a senha de um usuário."""
    new_password: str
# ------------------------------------

# Schemas de Dashboard
class DashboardStats(BaseModel):
    total_cameras: int
    online_cameras: int
    sightings_today: int
    alerts_24h: int

# Schemas de Ticket
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

# --- NOVO: Schemas de Log de Auditoria ---
class AuditLogBase(BaseModel):
    action: str
    target_id: Optional[int] = None
    target_type: Optional[str] = None
    details: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: int
    timestamp: datetime
    actor_id: int
    actor: UserBase # NOVO: Inclui os dados do ator na resposta

    class Config:
        from_attributes = True