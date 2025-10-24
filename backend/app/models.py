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
    # --- ADIÇÃO AQUI ---
    api_keys = relationship("ApiKey", back_populates="client", cascade="all, delete-orphan")
    blacklist_entries = relationship("BlacklistedPlate", back_populates="client", cascade="all, delete-orphan")

#  Schemas de Câmera
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    password_change_required = Column(Boolean, default=False, nullable=False) # NOVO
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

# --- ADIÇÃO DA CLASSE FALTANTE ABAIXO ---
class BlacklistedPlate(Base):
    __tablename__ = "blacklisted_plates"
    
    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, index=True, nullable=False)
    reason = Column(String, nullable=True) # Motivo da inclusão na lista
    created_at = Column(DateTime, default=datetime.utcnow)
    
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="blacklist_entries")

# --- ADIÇÃO DA CLASSE FALTANTE ABAIXO: ApiKey ---
class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True) # Nome descritivo para a chave (ex: "AI Processor Key")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True) # Chave pode ser global (client_id=None) ou específica de um cliente
    client = relationship("Client", back_populates="api_keys")

# --- NOVO: Modelo para Log de Auditoria ---
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    action = Column(String, nullable=False) # Ex: "USER_CREATED", "PASSWORD_RESET"
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Quem realizou a ação
    target_id = Column(Integer, nullable=True) # ID do objeto afetado (ex: ID do usuário criado/resetado)
    target_type = Column(String, nullable=True) # Tipo do objeto afetado (ex: "User")
    details = Column(String, nullable=True) # Detalhes adicionais em JSON ou texto

    actor = relationship("User") # Relacionamento com o usuário que realizou a ação