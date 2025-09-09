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
)
from sqlalchemy.orm import relationship
from .database import Base  # <--- Certifique-se que esta linha está correta

class UserRole(enum.Enum):
    ADMIN = "admin"
    CLIENT_ADMIN = "client_admin"
    CLIENT_USER = "client_user"

# ... (o resto do seu ficheiro models.py continua igual)
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="client", cascade="all, delete-orphan")
    cameras = relationship("Camera", back_populates="client", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.CLIENT_USER, nullable=False)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="users")

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    rtsp_url = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="cameras")
    sightings = relationship("VehicleSighting", back_populates="camera", cascade="all, delete-orphan")

class VehicleSighting(Base):
    __tablename__ = "vehicle_sightings"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    license_plate = Column(String, index=True)
    image_filename = Column(String)

    camera_id = Column(Integer, ForeignKey("cameras.id"))
    camera = relationship("Camera", back_populates="sightings")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, unique=True)
    phone = Column(String, nullable=True)
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)