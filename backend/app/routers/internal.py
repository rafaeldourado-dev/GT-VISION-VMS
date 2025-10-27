import json
import redis 
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..dependencies import get_db, get_redis_client
from .. import models, schemas, crud
from ..utils.email import send_blacklist_alert_email

router = APIRouter(
    prefix="/internal",
    tags=["Internal API"],
    responses={404: {"description": "Not found"}},
)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header), db: AsyncSession = Depends(get_db)):
    """Dependência para validar a chave de API interna."""
    # A chave de API agora é buscada do banco de dados para suportar múltiplos clientes
    db_api_key = await crud.validate_api_key(db, api_key)
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return db_api_key

@router.get("/cameras", 
            response_model=List[Dict[str, Any]], # Alterado para refletir a nova estrutura
            dependencies=[Depends(get_api_key)])
async def get_all_active_cameras_internal(db: AsyncSession = Depends(get_db)):
    """
    Retorna uma lista de todas as câmaras ativas no sistema.
    Para uso interno pelo AI-Processor.
    --- MODIFICADO ---
    Agora, esta rota retorna a URL do stream passando pelo MediaMTX,
    garantindo uma conexão interna e estável para o processador.
    """
    result = await db.execute(
        select(models.Camera).filter(models.Camera.is_active == True)
    )
    cameras = result.scalars().all()

    # Constrói a resposta com a URL interna do MediaMTX
    cameras_with_internal_url: List[Dict[str, Any]] = []
    for cam in cameras:
        camera_data = schemas.Camera.model_validate(cam).model_dump()
        # O AI-Processor vai usar a URL RTSP original da câmera, sem passar pelo MediaMTX
        camera_data["rtsp_url"] = cam.rtsp_url
        cameras_with_internal_url.append(camera_data)

    return cameras_with_internal_url

# --- ROTA PARA CRIAR SIGHTINGS (CORRIGIDA E NO LOCAL CERTO) ---
@router.post("/sightings", 
             response_model=schemas.VehicleSighting, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_api_key)])
async def create_sighting_internal(
    sighting: schemas.VehicleSightingCreate,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client) # <-- AGORA FUNCIONA
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

    # Verifica se a placa está na lista negra do cliente associado à câmera
    blacklisted_plate = await crud.get_blacklisted_plate_by_plate(
        db, license_plate=sighting.license_plate, client_id=camera.client_id
    )

    if blacklisted_plate:
        # Se estiver na lista negra, busca os admins do cliente para notificar
        # 1. Envio de e-mail
        admins_to_notify = await crud.get_admins_by_client(db, client_id=camera.client_id)
        for admin in admins_to_notify:
            await send_blacklist_alert_email(
                recipient_email=admin.email, sighting=new_sighting
            )
        
        # 2. Publicação no Redis para notificação em tempo real via WebSocket
        alert_message = {
            "type": "blacklist_alert",
            "plate": new_sighting.license_plate,
            "camera_name": new_sighting.camera.name,
            "timestamp": new_sighting.timestamp.isoformat(),
        }
        channel = f"alerts:{camera.client_id}"
        await redis_client.publish(channel, json.dumps(alert_message))

    return new_sighting
