import enum
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Enum as SQLAlchemyEnum,
    Float,
    func,
)
from sqlalchemy.orm import relationship
from .database import Base  

# Enumeração para os papéis dos usuários
class UserRole(enum.Enum):
    ADMIN = "admin"
    CLIENT_ADMIN = "client_admin"
    CLIENT_USER = "client_user"

# Modelos de Banco de Dados
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="client", cascade="all, delete-orphan")
    cameras = relationship("Camera", back_populates="client", cascade="all, delete-orphan")

#  Schemas de Câmera
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.CLIENT_USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="users")
    tickets = relationship("Ticket", back_populates="owner")


class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    rtsp_url = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="cameras")
    sightings = relationship("VehicleSighting", back_populates="camera", cascade="all, delete-orphan")

# --- ALTERAÇÕES AQUI ---
class VehicleSighting(Base):
    __tablename__ = "vehicle_sightings"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    license_plate = Column(String, index=True)
    
    # NOVOS CAMPOS PARA O MVP
    vehicle_color = Column(String, index=True, nullable=True)
    vehicle_model = Column(String, index=True, nullable=True)
    image_path = Column(String, nullable=True) # Nome do ficheiro da imagem

    camera_id = Column(Integer, ForeignKey("cameras.id"))
    camera = relationship("Camera", back_populates="sightings")
# -----------------------

# Schemas de Lead
class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, unique=True)
    phone = Column(String, nullable=True)
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)

# Schemas de Ticket
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    description = Column(String)
    status = Column(String, default="open")
    priority = Column(String, default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tickets")