from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, time
from typing import Optional, List
from sqlalchemy.orm import selectinload
import json # NOVO: Para serializar/desserializar dados de/para Redis
import redis.asyncio as redis # NOVO: Importa o cliente Redis assíncrono

from .config import settings # CORRIGIDO: De ..config para .config
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
        password_change_required=True, # NOVO: Força a troca de senha no primeiro login
        role=user.role,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_users_by_client(db: AsyncSession, client_id: int) -> List[models.User]:
    """Retorna uma lista de todos os usuários para um determinado cliente."""
    result = await db.execute(
        select(models.User)
        .filter(models.User.client_id == client_id)
        .order_by(models.User.full_name)
    )
    return result.scalars().all()

async def update_user_password(db: AsyncSession, user: models.User, new_password: str) -> models.User:
    """
    Atualiza a senha de um usuário específico.
    """
    hashed_password = security.get_password_hash(new_password)
    user.hashed_password = hashed_password
    user.password_change_required = True # NOVO: Força a troca de senha após reset do admin
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(db: AsyncSession, user: models.User, user_update: schemas.UserUpdate) -> models.User:
    """
    Atualiza os detalhes de um usuário (nome, email, status, role).
    """
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: int):
    """
    Deleta um usuário do banco de dados.
    """
    user = await get_user(db, user_id=user_id)
    if user:
        await db.delete(user)
        await db.commit()
    return

async def update_own_password(db: AsyncSession, user: models.User, new_password: str) -> models.User:
    """
    Atualiza a senha do próprio usuário e desativa a flag de troca obrigatória.
    """
    hashed_password = security.get_password_hash(new_password)
    user.hashed_password = hashed_password
    user.password_change_required = False # NOVO: Desativa a obrigatoriedade
    await db.commit()
    await db.refresh(user)
    return user

async def create_audit_log(
    db: AsyncSession,
    actor_id: int,
    action: str,
    target_id: Optional[int] = None,
    target_type: Optional[str] = None,
    details: Optional[str] = None
) -> models.AuditLog:
    db_log = models.AuditLog(actor_id=actor_id, action=action, target_id=target_id, target_type=target_type, details=details)
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def get_audit_logs_by_client(
    db: AsyncSession,
    client_id: int,
    skip: int = 0,
    limit: int = 100,
    actor_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """
    Busca os logs de auditoria para um cliente específico, com paginação e filtros.
    """
    # Query base
    query = (
        select(models.AuditLog)
        .join(models.User, models.AuditLog.actor_id == models.User.id)
        .filter(models.User.client_id == client_id)
    )

    # Aplicar filtros
    if actor_id:
        query = query.filter(models.AuditLog.actor_id == actor_id)
    if action:
        query = query.filter(models.AuditLog.action == action)
    if start_date:
        query = query.filter(models.AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(models.AuditLog.timestamp < (end_date + timedelta(days=1)))

    # Query para contar o total de itens com os filtros
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Aplicar ordenação e paginação para buscar os itens da página
    paginated_query = query.options(selectinload(models.AuditLog.actor)).order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    return {"items": items, "total": total}

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

async def create_client_camera(db: AsyncSession, camera: schemas.CameraCreate, client_id: int, redis_client: redis.Redis) -> models.Camera:
    """Cria uma nova câmera para um cliente de forma explícita e invalida o cache de estatísticas."""
    db_camera = models.Camera(
        name=camera.name,
        rtsp_url=camera.rtsp_url,
        is_active=camera.is_active,
        latitude=camera.latitude,
        longitude=camera.longitude,
        client_id=client_id
    )
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)

    # NOVO: Invalidação do Cache-Aside (Write-Through)
    cache_key = f"dashboard_stats:{client_id}"
    await redis_client.delete(cache_key) # Força a próxima leitura a ir para o DB

    return db_camera

async def update_camera(db: AsyncSession, camera_id: int, camera_update: schemas.CameraUpdate, client_id: int, redis_client: redis.Redis) -> Optional[models.Camera]:
    """Atualiza uma câmera e invalida o cache de estatísticas."""
    camera = await get_camera_by_id(db, camera_id=camera_id)
    if camera and camera.client_id == client_id:
        update_data = camera_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(camera, field, value)
        
        await db.commit()
        await db.refresh(camera)

        # Invalidação do Cache-Aside
        cache_key = f"dashboard_stats:{client_id}"
        await redis_client.delete(cache_key)

        return camera
    return None

async def delete_camera(db: AsyncSession, camera_id: int, client_id: int, redis_client: redis.Redis):
    """Apaga uma câmera e invalida o cache de estatísticas."""
    camera = await get_camera_by_id(db, camera_id=camera_id)
    if camera:
        await db.delete(camera)
        await db.commit()
        
        # NOVO: Invalidação do Cache-Aside (Write-Through)
        cache_key = f"dashboard_stats:{client_id}"
        await redis_client.delete(cache_key) # Força a próxima leitura a ir para o DB

    return camera
# endregion

# region CRUD ApiKey
async def create_api_key(db: AsyncSession, api_key: schemas.ApiKeyCreate) -> models.ApiKey:
    """Cria uma nova chave de API."""
    db_api_key = models.ApiKey(
        key=api_key.key,
        name=api_key.name,
        is_active=api_key.is_active,
        client_id=api_key.client_id
    )
    db.add(db_api_key)
    await db.commit()
    await db.refresh(db_api_key)
    return db_api_key

async def validate_api_key(db: AsyncSession, api_key_str: str) -> Optional[models.ApiKey]:
    """
    Valida uma chave de API interna.
    Retorna o objeto ApiKey se for válido e ativo, caso contrário, None.
    """
    result = await db.execute(
        select(models.ApiKey).filter(models.ApiKey.key == api_key_str, models.ApiKey.is_active == True)
    )
    return result.scalars().first()
# endregion

# region CRUD VehicleSighting
async def create_vehicle_sighting(db: AsyncSession, sighting: schemas.VehicleSightingCreate) -> models.VehicleSighting:
    db_sighting = models.VehicleSighting(**sighting.dict())
    db.add(db_sighting)
    # A acurácia já estará no sighting.dict() se o schema for atualizado
    await db.commit()
    await db.refresh(db_sighting)
    return db_sighting

async def get_sightings_by_client(
    db: AsyncSession, 
    client_id: int, 
    skip: int = 0, 
    limit: int = 100,
    license_plate: Optional[str] = None,
    camera_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    vehicle_color: Optional[str] = None,
    vehicle_model: Optional[str] = None,
) -> dict:
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
    if camera_id:
        query = query.filter(models.Camera.id == camera_id)
    if start_date:
        query = query.filter(models.VehicleSighting.timestamp >= start_date)
    if end_date:
        query = query.filter(models.VehicleSighting.timestamp <= end_date)
    if vehicle_color:
        query = query.filter(models.VehicleSighting.vehicle_color.ilike(f"%{vehicle_color}%"))
    if vehicle_model:
        query = query.filter(models.VehicleSighting.vehicle_model.ilike(f"%{vehicle_model}%"))

    # Primeiro, fazemos uma query para contar o total de resultados com os filtros aplicados
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Depois, aplicamos a ordenação e a paginação para buscar apenas os itens da página atual
    paginated_query = query.order_by(models.VehicleSighting.timestamp.desc()).offset(skip).limit(limit)
    
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    return {"items": items, "total": total}

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

    # 1. Tentar ler no Cache (Cache-Aside Read)
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        try:
            return json.loads(cached_data) # Cache Hit
        except json.JSONDecodeError:
            # Em caso de erro de desserialização, continuar para o DB
            pass

    # 2. Se falhar (Cache Miss), consultar o DB
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

    # 3. Gravar no Cache antes de retornar
    await redis_client.set(
        cache_key,
        json.dumps(stats),
        ex=settings.REDIS_CACHE_TTL_SECONDS # Define o TTL do cache
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