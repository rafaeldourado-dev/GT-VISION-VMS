from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, time
from typing import Optional

from . import models, schemas, security

# region CRUD Client (Organização)
async def get_client(db: AsyncSession, client_id: int) -> Optional[models.Client]:
    """Busca um cliente pelo seu ID."""
    result = await db.execute(select(models.Client).filter(models.Client.id == client_id))
    return result.scalars().first()

async def get_client_by_name(db: AsyncSession, name: str) -> Optional[models.Client]:
    """Busca um cliente pelo seu nome."""
    result = await db.execute(select(models.Client).filter(models.Client.name == name))
    return result.scalars().first()

async def create_client(db: AsyncSession, client: schemas.ClientCreate) -> models.Client:
    """Cria um novo cliente."""
    db_client = models.Client(name=client.name)
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client
# endregion

# region CRUD User
async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Busca um usuário pelo seu ID."""
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    """Busca um usuário pelo seu nome de usuário (que é o email)."""
    # Assumimos que o nome de usuário está guardado no campo de email
    result = await db.execute(select(models.User).filter(models.User.email == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """Busca um usuário pelo seu email."""
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    """Cria um novo usuário."""
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        client_id=user.client_id,
        role=user.role,
        full_name=user.full_name,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
# endregion

# region CRUD Camera
async def get_camera_by_id(db: AsyncSession, camera_id: int) -> Optional[models.Camera]:
    """Busca uma câmera pelo seu ID."""
    result = await db.execute(select(models.Camera).filter(models.Camera.id == camera_id))
    return result.scalars().first()

async def get_cameras_by_client(db: AsyncSession, client_id: int, skip: int = 0, limit: int = 100):
    """Lista as câmeras de um cliente específico."""
    result = await db.execute(
        select(models.Camera)
        .filter(models.Camera.client_id == client_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_client_camera(db: AsyncSession, camera: schemas.CameraCreate, client_id: int) -> models.Camera:
    """Cria uma nova câmera para um cliente."""
    db_camera = models.Camera(**camera.dict(), client_id=client_id)
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    return db_camera

async def update_camera(db: AsyncSession, camera: models.Camera, update_data: schemas.CameraUpdate) -> models.Camera:
    """Atualiza os dados de uma câmera."""
    update_data_dict = update_data.dict(exclude_unset=True)
    for key, value in update_data_dict.items():
        setattr(camera, key, value)

    await db.commit()
    await db.refresh(camera)
    return camera

async def delete_camera(db: AsyncSession, camera_id: int):
    """Deleta uma câmera do banco de dados."""
    camera = await get_camera_by_id(db, camera_id=camera_id)
    if camera:
        await db.delete(camera)
        await db.commit()
    return camera
# endregion

# region CRUD VehicleSighting
async def create_vehicle_sighting(db: AsyncSession, sighting: schemas.VehicleSightingCreate) -> models.VehicleSighting:
    """Cria um novo registro de detecção de veículo."""
    db_sighting = models.VehicleSighting(**sighting.dict())
    db.add(db_sighting)
    await db.commit()
    await db.refresh(db_sighting)
    return db_sighting

async def get_sightings_by_client(db: AsyncSession, client_id: int, skip: int = 0, limit: int = 100):
    """Lista as detecções de um cliente específico."""
    result = await db.execute(
        select(models.VehicleSighting)
        .join(models.Camera)
        .filter(models.Camera.client_id == client_id)
        .order_by(models.VehicleSighting.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
# endregion

# region CRUD Lead (CRM)
async def get_leads(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Lista todos os leads do CRM."""
    result = await db.execute(select(models.Lead).offset(skip).limit(limit))
    return result.scalars().all()

async def create_lead(db: AsyncSession, lead: schemas.LeadCreate) -> models.Lead:
    """Cria um novo lead no CRM."""
    db_lead = models.Lead(**lead.dict())
    db.add(db_lead)
    await db.commit()
    await db.refresh(db_lead)
    return db_lead
# endregion

# region Dashboard Stats
async def get_dashboard_stats(db: AsyncSession, client_id: int) -> dict:
    """Busca estatísticas agregadas para o dashboard de um cliente."""
    today_start = datetime.combine(datetime.utcnow().date(), time.min)

    # Total de câmeras
    total_cameras_query = select(func.count(models.Camera.id)).filter(models.Camera.client_id == client_id)
    total_cameras_result = await db.execute(total_cameras_query)
    total_cameras = total_cameras_result.scalar_one()

    # Câmeras ativas
    active_cameras_query = select(func.count(models.Camera.id)).filter(
        models.Camera.client_id == client_id, models.Camera.is_active == True
    )
    active_cameras_result = await db.execute(active_cameras_query)
    active_cameras = active_cameras_result.scalar_one()

    # Detecções de hoje
    total_sightings_today_query = select(func.count(models.VehicleSighting.id)).join(models.Camera).filter(
        models.Camera.client_id == client_id,
        models.VehicleSighting.timestamp >= today_start
    )
    total_sightings_today_result = await db.execute(total_sightings_today_query)
    total_sightings_today = total_sightings_today_result.scalar_one()

    # Retorna um dicionário com os nomes de campo que o frontend espera
    return {
        "total_cameras": total_cameras,
        "online_cameras": active_cameras,      # Renomeado de 'active_cameras'
        "sightings_today": total_sightings_today, # Renomeado de 'total_sightings_today'
        "alerts_24h": 0,                        # Valor fixo, pois a lógica não existe
    }
# endregion