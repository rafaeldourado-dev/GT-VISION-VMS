import json
import redis 
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# --- INÍCIO DA CORREÇÃO (Etapa 1B) ---
# Importa 'settings' para ler a API Key do .env
from ..dependencies import get_db, get_redis_client
from ..config import settings 
# --- FIM DA CORREÇÃO ---
from .. import models, schemas, crud
from ..utils.email import send_blacklist_alert_email

router = APIRouter(
    # O prefixo /api/v1 é adicionado em main.py
    # Então o prefixo aqui deve ser /internal
    prefix="/internal", 
    tags=["Internal API"],
    responses={404: {"description": "Not found"}},
)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# --- INÍCIO DA CORREÇÃO (Etapa 1B) ---
# Substituída a lógica de 'crud.validate_api_key' pela lógica simples
# que compara a chave com o .env (ADMIN_API_KEY)
async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Dependência para validar a chave de API interna (Método Simples).
    Verifica se a chave enviada corresponde à definida no .env.
    """
    if settings.ADMIN_API_KEY and api_key == settings.ADMIN_API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
# --- FIM DA CORREÇÃO ---


@router.get("/cameras", 
            response_model=List[Dict[str, Any]],
            dependencies=[Depends(get_api_key)]) # Agora usa a API Key simples
async def get_all_active_cameras_internal(db: AsyncSession = Depends(get_db)):
    """
    Retorna uma lista de todas as câmaras ativas no sistema.
    Para uso interno pelo AI-Processor.
    O AI-Processor vai usar a URL RTSP original da câmera.
    """
    result = await db.execute(
        select(models.Camera).filter(models.Camera.is_active == True)
    )
    cameras = result.scalars().all()

    cameras_with_internal_url: List[Dict[str, Any]] = []
    for cam in cameras:
        # Usamos o schema para converter o modelo, mas garantimos que a rtsp_url é a original
        camera_data = schemas.Camera.model_validate(cam).model_dump()
        camera_data["rtsp_url"] = cam.rtsp_url 
        cameras_with_internal_url.append(camera_data)

    return cameras_with_internal_url

@router.post("/sightings", 
             response_model=schemas.VehicleSighting, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_api_key)]) # Agora usa a API Key simples
async def create_sighting_internal(
    sighting: schemas.VehicleSightingCreate,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.asyncio.Redis = Depends(get_redis_client) # Corrigido para redis.asyncio.Redis se for assíncrono
):
    """
    Cria um novo avistamento de veículo.
    (Usado pelo AI-Processor para submeter novas detecções)
    """
    camera = await crud.get_camera_by_id(db, camera_id=sighting.camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Câmara com id {sighting.camera_id} não encontrada.",
        )
            
    new_sighting = await crud.create_vehicle_sighting(db=db, sighting=sighting)

    # Verifica se a placa está na lista negra
    blacklisted_plate = await crud.get_blacklisted_plate_by_plate(
        db, license_plate=sighting.license_plate, client_id=camera.client_id
    )

    if blacklisted_plate:
        # 1. Envio de e-mail
        admins_to_notify = await crud.get_admins_by_client(db, client_id=camera.client_id)
        for admin in admins_to_notify:
            await send_blacklist_alert_email(
                recipient_email=admin.email, sighting=new_sighting
            )
        
        # 2. Publicação no Redis para notificação em tempo real
        alert_message = {
            "type": "blacklist_alert",
            "plate": new_sighting.license_plate,
            "camera_name": new_sighting.camera.name,
            "timestamp": new_sighting.timestamp.isoformat(),
        }
        channel = f"alerts:{camera.client_id}"
        # Garante que a publicação é 'await' se o redis_client for assíncrono
        await redis_client.publish(channel, json.dumps(alert_message))

    return new_sighting