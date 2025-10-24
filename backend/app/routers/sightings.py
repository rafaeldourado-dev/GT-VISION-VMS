from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession  # <-- FIX: Added import

from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/sightings",
    tags=["Detecções"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

class PaginatedSightings(BaseModel):
    items: List[schemas.VehicleSighting]
    total: int

@router.get("/", response_model=PaginatedSightings)
async def read_sightings(
    skip: int = 0,
    limit: int = 100,
    license_plate: Optional[str] = None,
    camera_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Lista as detecções para o cliente do usuário autenticado, com filtros avançados.
    """
    sightings = await crud.get_sightings_by_client(
        db, client_id=current_user.client_id, skip=skip, limit=limit,
        license_plate=license_plate, camera_id=camera_id,
        start_date=start_date, end_date=end_date
    )
    return sightings
# <-- FIX: Removed stray '}' from here