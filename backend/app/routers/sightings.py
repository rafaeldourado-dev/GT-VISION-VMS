from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, get_current_user
from .. import crud, models, schemas

router = APIRouter(
    prefix="/sightings",
    tags=["Detecções"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.VehicleSightingResponse])
async def read_sightings(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    license_plate: Optional[str] = None,
    vehicle_color: Optional[str] = None,
    vehicle_model: Optional[str] = None,
):
    """
    Recupera uma lista de avistamentos de veículos para o cliente do utilizador,
    com filtros opcionais.
    """
    sightings = await crud.get_sightings_by_client(
        db=db, 
        client_id=current_user.client_id, 
        skip=skip, 
        limit=limit,
        license_plate=license_plate,
        vehicle_color=vehicle_color,
        vehicle_model=vehicle_model
    )
    return sightings