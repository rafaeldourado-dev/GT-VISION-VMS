from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .. import crud, schemas, models
from ..dependencies import get_db, get_current_client_admin

router = APIRouter(
    prefix="/blacklist",
    tags=["Blacklist"],
    dependencies=[Depends(get_current_client_admin)] # Protege todas as rotas
)

@router.post("/", response_model=schemas.BlacklistedPlate, status_code=status.HTTP_201_CREATED)
async def add_plate_to_blacklist(
    plate_in: schemas.BlacklistedPlateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_client_admin)
):
    """
    Adiciona uma nova placa à lista negra do cliente.
    """
    # Associa a placa ao cliente do admin que está a fazer a requisição
    db_plate = await crud.get_blacklisted_plate_by_plate(db, license_plate=plate_in.license_plate, client_id=current_user.client_id)
    if db_plate:
        raise HTTPException(status_code=400, detail="Placa já está na lista negra.")
    
    return await crud.create_blacklisted_plate(db=db, plate=plate_in, client_id=current_user.client_id)

@router.get("/", response_model=List[schemas.BlacklistedPlate])
async def get_client_blacklist(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_client_admin)
):
    """
    Retorna todas as placas na lista negra do cliente.
    """
    return await crud.get_blacklisted_plates_by_client(db, client_id=current_user.client_id)

@router.delete("/{plate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_plate_from_blacklist(
    plate_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_client_admin)
):
    """
    Remove uma placa da lista negra.
    """
    plate_to_delete = await crud.get_blacklisted_plate_by_id(db, plate_id=plate_id)
    
    if not plate_to_delete or plate_to_delete.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Placa não encontrada na lista negra.")

    await crud.delete_blacklisted_plate(db=db, plate_id=plate_id)
    return