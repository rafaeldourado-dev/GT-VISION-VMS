from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, dependencies, models, messaging

router = APIRouter(prefix="/cameras", tags=["cameras"])

@router.post("/", response_model=schemas.Camera, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera: schemas.CameraCreate,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    """
    Cria uma nova câmera para o cliente do usuário logado.
    Se a câmera for criada como ativa, envia um comando 'start' para o processador.
    """
    new_camera = await crud.create_client_camera(db=db, camera=camera, client_id=current_user.client_id)
    
    # Se a câmera já começa ativa, manda a mensagem para iniciar o processamento
    if new_camera.is_active:
        camera_schema = schemas.Camera.from_orm(new_camera)
        messaging.publish_camera_command(action="start", camera=camera_schema)
        
    return new_camera

@router.get("/", response_model=List[schemas.Camera])
async def read_cameras(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    """
    Lista todas as câmeras associadas ao cliente do usuário logado.
    """
    cameras = await crud.get_cameras_by_client(db, client_id=current_user.client_id, skip=skip, limit=limit)
    return cameras

@router.put("/{camera_id}", response_model=schemas.Camera)
async def update_camera(
    camera_id: int,
    camera_update: schemas.CameraUpdate,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    """
    Atualiza uma câmera.
    Envia comandos 'start' ou 'stop' se o status 'is_active' for alterado.
    """
    db_camera = await crud.get_camera_by_id(db, camera_id=camera_id)
    
    if not db_camera or db_camera.client_id != current_user.client_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    old_status = db_camera.is_active
    updated_camera = await crud.update_camera(db=db, camera=db_camera, update_data=camera_update)
    new_status = updated_camera.is_active
    
    # Lógica para enviar mensagem apenas se o status de ativação mudar
    if old_status != new_status:
        action = "start" if new_status else "stop"
        camera_schema = schemas.Camera.from_orm(updated_camera)
        messaging.publish_camera_command(action=action, camera=camera_schema)
        
    return updated_camera

@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    """
    Deleta uma câmera.
    Envia um comando 'stop' para garantir que o processamento seja interrompido.
    """
    db_camera = await crud.get_camera_by_id(db, camera_id=camera_id)

    if not db_camera or db_camera.client_id != current_user.client_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    # Garante que o processamento pare antes de deletar
    if db_camera.is_active:
        camera_schema = schemas.Camera.from_orm(db_camera)
        messaging.publish_camera_command(action="stop", camera=camera_schema)

    await crud.delete_camera(db=db, camera_id=camera_id)
    return