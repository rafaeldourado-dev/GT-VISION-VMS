from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, time
from typing import Optional, List
from sqlalchemy.orm import selectinload
import json
import redis.asyncio as redis

from .config import settings
from . import models, schemas, security

# region CRUD Client (Organização)
async def get_client(db: AsyncSession, client_id: int) -> Optional[models.Client]:
    result = await db.execute(select(models.Client).filter(models.Client.id == client_id))
    return result.scalars().first()

async def get_client_by_name(db: AsyncSession, name: str) -> Optional[models.Client]:
    result = await db.execute(select(models.Client).filter(models.Client.name == name))
    return result.scalars().first()

async def create_client(db: AsyncSession, client: schemas.ClientCreate) -> models.Client:
    db_client = models.Client(**client.dict())
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client
# endregion

# region CRUD User
async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        client_id=user.client_id,
        role=user.role,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
# endregion

# region CRUD Camera
async def get_camera_by_id(db: AsyncSession, camera_id: int) -> Optional[models.Camera]:
    result = await db.execute(select(models.Camera).filter(models.Camera.id == camera_id))
    return result.scalars().first()

async def get_cameras_by_client(db: AsyncSession, client_id: int, skip: int = 0, limit: int = 100) -> List[models.Camera]:
    result = await db.execute(
        select(models.Camera)
        .filter(models.Camera.client_id == client_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

# --- NOVA FUNÇÃO ADICIONADA ---
async def get_cameras_by_type(db: AsyncSession, camera_type: str) -> List[models.Camera]:
    """Retorna todas as câmeras ativas de um tipo específico."""
    result = await db.execute(
        select(models.Camera)
        .filter(models.Camera.camera_type == camera_type, models.Camera.is_active == True)
    )
    return result.scalars().all()
# -----------------------------

# --- FUNÇÃO ATUALIZADA ---
async def create_client_camera(db: AsyncSession, camera: schemas.CameraCreate, client_id: int, redis_client: redis.Redis) -> models.Camera:
    """Cria uma nova câmera para um cliente de forma explícita e invalida o cache de estatísticas."""
    db_camera = models.Camera(
        name=camera.name,
        rtsp_url=camera.rtsp_url,
        camera_type=camera.camera_type, # <-- Campo adicionado
        is_active=camera.is_active,
        latitude=camera.latitude,
        longitude=camera.longitude,
        client_id=client_id
    )
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    cache_key = f"dashboard_stats:{client_id}"
    await redis_client.delete(cache_key)
    return db_camera
# -------------------------

async def delete_camera(db: AsyncSession, camera_id: int, client_id: int, redis_client: redis.Redis):
    """Apaga uma câmera e invalida o cache de estatísticas."""
    camera = await get_camera_by_id(db, camera_id=camera_id)
    if camera:
        await db.delete(camera)
        await db.commit()
        cache_key = f"dashboard_stats:{client_id}"
        await redis_client.delete(cache_key)
    return camera
# endregion

# region CRUD VehicleSighting
async def create_vehicle_sighting(
    db: AsyncSession,
    sighting: schemas.VehicleSightingCreate,
    camera_id: Optional[int] = None
) -> models.VehicleSighting:
    """
    Cria um novo avistamento.
    Esta função unificada funciona tanto para o 'coletor' (que passa camera_id como argumento)
    quanto para o 'internal' (que passa camera_id dentro do schema).
    """
    # 1. Determina o ID da câmera
    final_camera_id = camera_id if camera_id is not None else sighting.camera_id
    if final_camera_id is None:
        raise ValueError("O ID da câmera é obrigatório para criar um avistamento.")

    # 2. Prepara os dados do schema, removendo o camera_id opcional
    sighting_data = sighting.dict(exclude={"camera_id"})

    # 3. Mapeia o campo do schema (plate_image_url) para o do modelo (image_path)
    if 'plate_image_url' in sighting_data:
        sighting_data['image_path'] = sighting_data.pop('plate_image_url')

    # 4. Cria a instância do modelo com todos os dados corretos
    db_sighting = models.VehicleSighting(
        **sighting_data,
        camera_id=final_camera_id
    )
    
    db.add(db_sighting)
    await db.commit()
    await db.refresh(db_sighting)
    return db_sighting


async def get_sightings_by_client(
    db: AsyncSession, 
    client_id: int, 
    skip: int = 0, 
    limit: int = 100,
    license_plate: Optional[str] = None,
    vehicle_color: Optional[str] = None,
    vehicle_model: Optional[str] = None,
) -> List[models.VehicleSighting]:
    """
    Lista as detecções de um cliente, com filtros opcionais.
    """
    query = (
        select(models.VehicleSighting)
        .join(models.Camera)
        .filter(models.Camera.client_id == client_id)
        .options(selectinload(models.VehicleSighting.camera))
    )

    if license_plate:
        query = query.filter(models.VehicleSighting.license_plate.ilike(f"%{license_plate}%"))
    if vehicle_color:
        query = query.filter(models.VehicleSighting.vehicle_color.ilike(f"%{vehicle_color}%"))
    if vehicle_model:
        query = query.filter(models.VehicleSighting.vehicle_model.ilike(f"%{vehicle_model}%"))

    query = query.order_by(models.VehicleSighting.timestamp.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

# endregion

# region CRUD Lead (CRM)
async def create_lead(db: AsyncSession, lead: schemas.LeadCreate) -> models.Lead:
    db_lead = models.Lead(**lead.dict())
    db.add(db_lead)
    await db.commit()
    await db.refresh(db_lead)
    return db_lead
# endregion

# region Dashboard Stats
async def get_dashboard_stats(db: AsyncSession, client_id: int, redis_client: redis.Redis) -> dict:
    """
    Busca estatísticas do dashboard, implementando o padrão Cache-Aside.
    """
    cache_key = f"dashboard_stats:{client_id}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        try:
            return json.loads(cached_data)
        except json.JSONDecodeError:
            pass

    today_start = datetime.combine(datetime.utcnow().date(), time.min)

    total_cameras_query = select(func.count(models.Camera.id)).filter(models.Camera.client_id == client_id)
    total_cameras_result = await db.execute(total_cameras_query)
    total_cameras = total_cameras_result.scalar_one()

    active_cameras_query = select(func.count(models.Camera.id)).filter(
        models.Camera.client_id == client_id, models.Camera.is_active == True
    )
    active_cameras_result = await db.execute(active_cameras_query)
    active_cameras = active_cameras_result.scalar_one()

    total_sightings_today_query = select(func.count(models.VehicleSighting.id)).join(models.Camera).filter(
        models.Camera.client_id == client_id,
        models.VehicleSighting.timestamp >= today_start
    )
    total_sightings_today_result = await db.execute(total_sightings_today_query)
    total_sightings_today = total_sightings_today_result.scalar_one()

    stats = {
        "total_cameras": total_cameras,
        "online_cameras": active_cameras,
        "sightings_today": total_sightings_today,
        "alerts_24h": 0,
    }

    await redis_client.set(
        cache_key,
        json.dumps(stats),
        ex=settings.REDIS_CACHE_TTL_SECONDS
    )
    return stats
# endregion

# region CRUD Ticket
async def create_ticket(db: AsyncSession, ticket: schemas.TicketCreate, user_id: int) -> models.Ticket:
    db_ticket = models.Ticket(**ticket.dict(), owner_id=user_id)
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)
    return db_ticket

async def get_tickets_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Ticket]:
    result = await db.execute(
        select(models.Ticket)
        .filter(models.Ticket.owner_id == user_id)
        .order_by(models.Ticket.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_ticket_by_id(db: AsyncSession, ticket_id: int) -> Optional[models.Ticket]:
    result = await db.execute(select(models.Ticket).filter(models.Ticket.id == ticket_id))
    return result.scalars().first()

async def update_ticket(db: AsyncSession, ticket_id: int, ticket_update: schemas.TicketUpdate) -> Optional[models.Ticket]:
    ticket = await get_ticket_by_id(db, ticket_id)
    if ticket:
        update_data = ticket_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ticket, field, value)
        await db.commit()
        await db.refresh(ticket)
    return ticket

async def delete_ticket(db: AsyncSession, ticket_id: int) -> Optional[models.Ticket]:
    ticket = await get_ticket_by_id(db, ticket_id)
    if ticket:
        await db.delete(ticket)
        await db.commit()
    return ticket
# endregion