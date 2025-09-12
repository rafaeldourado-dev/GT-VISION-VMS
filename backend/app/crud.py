from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, time
from typing import Optional, List

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

# --- ALTERAÇÃO AQUI para ser mais explícito ---
async def create_client_camera(db: AsyncSession, camera: schemas.CameraCreate, client_id: int) -> models.Camera:
    """Cria uma nova câmera para um cliente de forma explícita."""
    db_camera = models.Camera(
        name=camera.name,
        rtsp_url=camera.rtsp_url,
        is_active=camera.is_active, # Passa o valor diretamente
        latitude=camera.latitude,
        longitude=camera.longitude,
        client_id=client_id
    )
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    return db_camera
# ---------------------------------------------

async def delete_camera(db: AsyncSession, camera_id: int):
    camera = await get_camera_by_id(db, camera_id=camera_id)
    if camera:
        await db.delete(camera)
        await db.commit()
    return camera
# endregion

# region CRUD VehicleSighting
async def create_vehicle_sighting(db: AsyncSession, sighting: schemas.VehicleSightingCreate) -> models.VehicleSighting:
    db_sighting = models.VehicleSighting(**sighting.dict())
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
async def get_dashboard_stats(db: AsyncSession, client_id: int) -> dict:
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

    return {
        "total_cameras": total_cameras,
        "online_cameras": active_cameras,
        "sightings_today": total_sightings_today,
        "alerts_24h": 0,
    }
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