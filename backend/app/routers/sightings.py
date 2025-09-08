from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .. import crud, schemas, dependencies, models

router = APIRouter(prefix="/sightings", tags=["sightings"])

@router.post("/vehicle", response_model=schemas.VehicleSighting)
async def create_sighting(
    sighting: schemas.VehicleSightingCreate,
    db: AsyncSession = Depends(dependencies.get_db),
):
    return await crud.create_vehicle_sighting(db=db, sighting=sighting)

# --- CORREÇÃO APLICADA AQUI ---
# A rota foi alterada de "/" para "" para corrigir o erro de redirecionamento 307.
@router.get("", response_model=List[schemas.VehicleSightingResponse])
async def read_sightings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(dependencies.get_db),
):
    # Assumimos o cliente com ID 1 para que a consulta funcione.
    db_sightings = await crud.get_sightings_by_client(
        db, client_id=1, skip=skip, limit=limit
    )
    
    response_data = [
        {
            "id": s.id,
            "plate": s.license_plate,
            "camera": {"name": s.camera.name if s.camera else "N/A"},
            "timestamp": s.timestamp,
        }
        for s in db_sightings
    ]
    return response_data