from sqlalchemy.orm import Session
from . import models
from datetime import datetime

def get_or_create_vehicle(db: Session, plate: str, color: str = None, model: str = None):
    """
    Busca um veículo pela placa. Se não existir, cria um novo.
    Se existir, atualiza a data do "last_seen".
    """
    db_vehicle = db.query(models.VehicleInfo).filter(models.VehicleInfo.license_plate == plate).first()
    
    if db_vehicle:
        # Se já existe, atualiza a data e retorna
        db_vehicle.last_seen = datetime.utcnow()
        if color:
            db_vehicle.vehicle_color = color
        if model:
            db_vehicle.vehicle_model = model
    else:
        # Se não existe, cria um novo
        db_vehicle = models.VehicleInfo(
            license_plate=plate,
            vehicle_color=color,
            vehicle_model=model
        )
        db.add(db_vehicle)
        
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle