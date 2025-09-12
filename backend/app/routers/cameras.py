from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..dependencies import get_db, get_current_user
from .. import crud, models, schemas

router = APIRouter(
    prefix="/cameras",
    tags=["Câmeras"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Camera, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera: schemas.CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Cria uma nova câmera para o cliente do usuário autenticado."""
    try:
        new_camera = await crud.create_client_camera(
            db=db, camera=camera, client_id=current_user.client_id
        )
        return new_camera
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uma câmera com esta URL RTSP já existe.",
        )

@router.get("/", response_model=List[schemas.Camera])
async def read_cameras(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Lista as câmaras pertencentes ao cliente do usuário autenticado."""
    cameras = await crud.get_cameras_by_client(
        db, client_id=current_user.client_id, skip=skip, limit=limit
    )
    return cameras

@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Apaga uma câmera."""
    camera_to_delete = await crud.get_camera_by_id(db, camera_id=camera_id)
    if not camera_to_delete or camera_to_delete.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")
    
    await crud.delete_camera(db, camera_id=camera_id)
    return None