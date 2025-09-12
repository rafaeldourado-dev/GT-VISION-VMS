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
        select(models.Camera).filter(models.Camera.is_active == True)
    )
    cameras = result.scalars().all()
    return cameras

# --- ROTA PARA CRIAR SIGHTINGS (CORRIGIDA E NO LOCAL CERTO) ---
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
    (Usado pelo AI-Processor para submeter novas detecções)
    """
    camera = await crud.get_camera_by_id(db, camera_id=sighting.camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Câmara com id {sighting.camera_id} não encontrada.",
        )
            
    return await crud.create_vehicle_sighting(db=db, sighting=sighting)