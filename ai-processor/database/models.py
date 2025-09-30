from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class VehicleInfo(Base):
    __tablename__ = "vehicle_info"

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, unique=True, index=True, nullable=False)
    vehicle_model = Column(String, nullable=True)
    vehicle_color = Column(String, nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)