# backend/app/routers/internal.py
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..dependencies import get_db
from .. import models, schemas, crud
from ..config import settings

router = APIRouter(
    prefix="/internal",
    tags=["Internal API"],
    responses={404: {"description": "Not found"}},
)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Dependência para validar a chave de API interna."""
    if api_key == settings.ADMIN_API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

@router.get("/cameras", 
            response_model=List[schemas.Camera], 
            dependencies=[Depends(get_api_key)])
async def get_all_active_cameras_internal(db: AsyncSession = Depends(get_db)):
    """
    Retorna uma lista de todas as câmaras ativas no sistema.
    Esta rota é para uso interno pelo AI-Processor.
    """
    result = await db.execute(
        select(models.Camera)
        .filter(models.Camera.camera_type == models.CameraType.GENERIC_RTSP, models.Camera.is_active == True) # Modificado para retornar apenas as genéricas
    )
    cameras = result.scalars().all()
    return cameras

# --- NOVA ROTA ADICIONADA ---
@router.get("/cameras/by_type/{camera_type}",
            response_model=List[schemas.Camera],
            dependencies=[Depends(get_api_key)])
async def get_cameras_by_type_internal(camera_type: str, db: AsyncSession = Depends(get_db)):
    """
    Retorna uma lista de câmeras ativas de um tipo específico.
    Usado pelo Event-Listener para encontrar as câmeras 'intelbras_push'.
    """
    # Validação simples do tipo de câmera
    try:
        models.CameraType(camera_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{camera_type}' não é um tipo de câmera válido."
        )
    
    cameras = await crud.get_cameras_by_type(db=db, camera_type=camera_type)
    return cameras
# -----------------------------

@router.post("/sightings", 
             response_model=schemas.VehicleSighting, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_api_key)])
async def create_sighting_internal(
    sighting: schemas.VehicleSightingCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Cria um novo avistamento de veículo.
    (Usado pelo AI-Processor ou Event-Processor para submeter novas detecções)
    """
    if sighting.camera_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O campo camera_id é obrigatório."
        )

    camera = await crud.get_camera_by_id(db, camera_id=sighting.camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Câmara com id {sighting.camera_id} não encontrada.",
        )
            
    return await crud.create_vehicle_sighting(db=db, sighting=sighting)