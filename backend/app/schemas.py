from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ==================================
# Schemas para Câmeras
# ==================================
class CameraBase(BaseModel):
    name: str
    location: Optional[str] = None
    url: str

class CameraCreate(CameraBase):
    pass

class Camera(CameraBase):
    id: int

    class Config:
        from_attributes = True

# ==================================
# Schemas para Avistamentos (Sightings)
# ==================================
class SightingBase(BaseModel):
    plate: str
    timestamp: datetime
    camera_id: int

class SightingCreate(SightingBase):
    pass

class Sighting(SightingBase):
    id: int

    class Config:
        from_attributes = True

# ==================================
# Schemas para Clientes (CRM)
# ==================================
class ClientBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int

    class Config:
        from_attributes = True

# ==================================
# Schemas para Usuários e Autenticação
# ==================================
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None