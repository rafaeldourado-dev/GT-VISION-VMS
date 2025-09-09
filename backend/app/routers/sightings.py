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
    # Este endpoint pode permanecer público se for o AI-Processor a enviar dados.
    return await crud.create_vehicle_sighting(db=db, sighting=sighting)

# --- CORREÇÃO APLICADA AQUI ---
# A rota foi alterada de "" para "/" para ser mais explícita e padrão.
# A dependência de autenticação foi reintroduzida.
@router.get("/", response_model=List[schemas.VehicleSightingResponse])
async def read_sightings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    # Usa o client_id do utilizador autenticado.
    db_sightings = await crud.get_sightings_by_client(
        db, client_id=current_user.client_id, skip=skip, limit=limit
    )
    
    # Adapta a resposta para o formato esperado pelo frontend.
    response_data = [
        schemas.VehicleSightingResponse(
            id=s.id,
            plate=s.license_plate,
            camera={"name": s.camera.name if s.camera else "N/A"},
            timestamp=s.timestamp,
        )
        for s in db_sightings
    ]
    return response_data