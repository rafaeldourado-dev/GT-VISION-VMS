from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, dependencies, models

router = APIRouter(prefix="/sightings", tags=["sightings"])

@router.post("/vehicle", response_model=schemas.VehicleSighting)
async def create_sighting(
    sighting: schemas.VehicleSightingCreate,
    db: AsyncSession = Depends(dependencies.get_db),
    # AINDA: Adicionar um token de API para o AI-Processor em vez de autenticação de usuário
):
    return await crud.create_vehicle_sighting(db=db, sighting=sighting)

@router.get("/", response_model=List[schemas.VehicleSighting])
async def read_sightings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    sightings = await crud.get_sightings_by_client(db, client_id=current_user.client_id, skip=skip, limit=limit)
    return sightings