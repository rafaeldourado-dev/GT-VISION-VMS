from sqlalchemy.orm import Session
from . import models, schemas, security

# User CRUD
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def regenerate_user_api_key(db: Session, user: models.User):
    user.api_key = security.generate_api_key()
    db.commit()
    db.refresh(user)
    return user

# Camera CRUD
def get_cameras_by_user(db: Session, user_id: int):
    return db.query(models.Camera).filter(models.Camera.owner_id == user_id).all()

def get_all_active_cameras(db: Session):
    return db.query(models.Camera).filter(models.Camera.ai_enabled == True).all()

def create_camera(db: Session, camera: schemas.CameraCreate, user_id: int):
    db_camera = models.Camera(**camera.model_dump(), owner_id=user_id)
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

# Vehicle Sighting CRUD
def create_sighting(db: Session, sighting_data: dict):
    db_sighting = models.VehicleSighting(**sighting_data)
    db.add(db_sighting)
    db.commit()
    db.refresh(db_sighting)
    return db_sighting

# --- Novas funções CRUD para o CRM ---
def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client