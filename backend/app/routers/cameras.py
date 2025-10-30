from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession  # <-- CHANGED
from sqlalchemy.exc import IntegrityError # <-- ADDED
from typing import List
import redis.asyncio as redis  # <-- ADDED

from app import crud, models, schemas # Re-adicionado o import de schemas
from app.dependencies import get_db, get_redis_client, get_current_active_user # Re-adicionado o import de dependências
from app.services.mediamtx_api import mediamtx_api
from app.services.thumbnail_service import generate_thumbnail_task

router = APIRouter(
    prefix="/cameras",
    tags=["cameras"],
    dependencies=[Depends(get_current_active_user)],
)

@router.post("/", response_model=schemas.Camera)
async def create_camera_with_mediamtx(  # <-- CHANGED
    camera: schemas.CameraCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Cria uma nova câmera no banco de dados e a registra no MediaMTX.
    """
    
    # --- INÍCIO DA CORREÇÃO ---
    # Verifica se a câmera já existe PARA ESTE CLIENTE
    existing_camera = await crud.get_camera_by_rtsp_url(
        db, 
        rtsp_url=camera.rtsp_url, 
        client_id=current_user.client_id  # <-- CORREÇÃO: Passa o ID do cliente atual
    )
    if existing_camera:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A camera with RTSP URL '{camera.rtsp_url}' already exists for your account." # <-- Mensagem de erro melhorada
        )
    # --- FIM DA CORREÇÃO ---

    try:
        # Cria a câmera no banco
        db_camera = await crud.create_client_camera(  # <-- CHANGED
            db=db, 
            camera=camera, 
            client_id=current_user.client_id,  # <-- ADDED
            redis_client=redis_client          # <-- ADDED
        )
    except IntegrityError:
        # --- CORREÇÃO DE RACE CONDITION (409) ---
        # Se uma requisição concorrente já criou, o commit falhará.
        await db.rollback() # Desfaz a transação
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A camera with RTSP URL '{camera.rtsp_url}' was created by a concurrent request."
        )
    except Exception as e:
        # --- NOVA CORREÇÃO (500) ---
        # Captura QUALQUER outro erro inesperado que possa acontecer
        await db.rollback() # Desfaz a transação
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while creating the camera: {str(e)}"
        )
    
    # Adiciona o path no MediaMTX
    try:
        await mediamtx_api.add_path(
            path_name=str(db_camera.id),
            config={
                "source": db_camera.rtsp_url,
                "sourceOnDemand": True
            }
        )
    except Exception as e:
        # Se falhar no mediamtx, reverte a criação da câmera
        await db.delete(db_camera)  # <-- CHANGED
        await db.commit()      # <-- CHANGED
        raise HTTPException(status_code=500, detail=f"Failed to add camera to MediaMTX: {e}") # Re-adicionado o raise HTTPException

    # Agenda a geração do thumbnail em background 
    background_tasks.add_task(generate_thumbnail_task, db_camera.id)
    
    return db_camera
@router.get("/", response_model=List[schemas.Camera])
async def read_cameras(  # <-- CHANGED
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Lista todas as câmeras.
    """
    # This was the function causing your specific error
    cameras = await crud.get_cameras_by_client(  # <-- CHANGED
        db, client_id=current_user.client_id, skip=skip, limit=limit
    )
    return cameras

@router.get("/{camera_id}", response_model=schemas.Camera)
async def read_camera(  # <-- CHANGED
    camera_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Obtém detalhes de uma câmera específica.
    """
    db_camera = await crud.get_camera_by_id(db, camera_id=camera_id)  # <-- CHANGED
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Security check
    if db_camera.client_id != current_user.client_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this camera")
        
    return db_camera

@router.put("/{camera_id}", response_model=schemas.Camera)
async def update_camera_with_mediamtx(  # <-- CHANGED
    camera_id: int,
    camera: schemas.CameraUpdate,  # <-- CHANGED (use CameraUpdate schema)
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Atualiza os detalhes de uma câmera e reconfigura no MediaMTX.
    """
    db_camera = await crud.get_camera_by_id(db, camera_id=camera_id)  # <-- CHANGED
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
        
    # Security check
    if db_camera.client_id != current_user.client_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this camera")

    # Atualiza a câmera no banco
    updated_camera = await crud.update_camera(  # <-- CHANGED
        db=db, 
        camera_id=camera_id, 
        camera_update=camera,
        client_id=current_user.client_id,  # <-- ADDED
        redis_client=redis_client          # <-- ADDED
    )
    
    if updated_camera is None:
         raise HTTPException(status_code=404, detail="Camera not found or update failed")

    # Reconfigura (edita) o path no MediaMTX
    try:
        await mediamtx_api.edit_path(
            path_name=str(camera_id),
            config={
                "source": updated_camera.rtsp_url,
                "sourceOnDemand": True
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update camera in MediaMTX: {e}")
    
    return updated_camera

@router.delete("/{camera_id}", response_model=schemas.Camera)
async def delete_camera_with_mediamtx(  # <-- CHANGED
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Remove uma câmera do banco de dados e do MediaMTX.
    """
    # Pega a câmera para verificar a permissão
    db_camera = await crud.get_camera_by_id(db, camera_id=camera_id)  # <-- CHANGED
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Security check
    if db_camera.client_id != current_user.client_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this camera")

    # Remove do MediaMTX primeiro
    try:
        await mediamtx_api.remove_path(path_name=str(camera_id))
    except Exception as e:
        print(f"Warning: Failed to remove path from MediaMTX (maybe it was already gone?): {e}")

    # Remove do banco
    deleted_camera = await crud.delete_camera(  # <-- CHANGED
        db=db, 
        camera_id=camera_id,
        client_id=current_user.client_id,  # <-- ADDED
        redis_client=redis_client          # <-- ADDED
    )
    
    if deleted_camera is None:
        # This should not happen if the get_camera_by_id passed, but good to have
        raise HTTPException(status_code=404, detail="Camera not found")

    return deleted_camera


@router.post("/{camera_id}/refresh_thumbnail", response_model=schemas.Camera)
async def refresh_camera_thumbnail(  # <-- CHANGED
    camera_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Solicita a geração de um novo thumbnail para a câmera.
    """
    camera = await crud.get_camera_by_id(db, camera_id=camera_id)  # <-- CHANGED
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Security check
    if camera.client_id != current_user.client_id:
        raise HTTPException(status_code=403, detail="Not authorized to refresh this camera")
    
    # Agenda a tarefa de atualização do thumbnail
    background_tasks.add_task(generate_thumbnail_task, camera_id)
    
    return camera