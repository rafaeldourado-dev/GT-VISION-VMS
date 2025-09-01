import enum
from datetime import datetime
from sqlalchemy import (Boolean, Column, Integer, String, ForeignKey, 
                        DateTime, Enum as SQLAlchemyEnum, Float)
from sqlalchemy.orm import relationship
from .database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CLIENT = "client"

class ClientStatus(str, enum.Enum):
    LEAD = "lead"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    INACTIVE = "inactive"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    api_key = Column(String, unique=True, index=True, nullable=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.CLIENT, nullable=False)
    
    cameras = relationship("Camera", back_populates="owner", cascade="all, delete-orphan")

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    rtsp_url = Column(String, unique=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ai_enabled = Column(Boolean, default=False, nullable=False)
    
    owner = relationship("User", back_populates="cameras")
    sightings = relationship("VehicleSighting", back_populates="camera", cascade="all, delete-orphan")

class VehicleSighting(Base):
    __tablename__ = "vehicle_sightings"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    license_plate = Column(String, index=True)
    vehicle_type = Column(String, nullable=True)
    vehicle_color = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    
    camera = relationship("Camera", back_populates="sightings")

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(ClientStatus), default=ClientStatus.LEAD, nullable=False)
    value = Column(Float, default=0.0)
    last_contact = Column(DateTime, default=datetime.utcnow)
    source = Column(String, nullable=True)
    assigned_to = Column(String, nullable=True)