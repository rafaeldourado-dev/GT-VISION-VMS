from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import redis.asyncio as redis # NOVO: Importa o cliente Redis
import cv2 # NOVO: Para capturar o frame da thumbnail
import asyncio # NOVO: Para operações assíncronas
from starlette.responses import Response # NOVO: Para retornar a imagem

from ..dependencies import get_db, get_current_user, get_redis_client, get_current_user_from_query_token # NOVO: Importa get_redis_client e get_current_user_from_query_token
from .. import crud, models, schemas, messaging

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
    redis_client: redis.Redis = Depends(get_redis_client), # NOVO: Adiciona o cliente Redis
):
    """Cria uma nova câmera para o cliente do usuário autenticado e invalida o cache de estatísticas."""
    try:
        new_camera = await crud.create_client_camera(
            db=db, camera=camera, client_id=current_user.client_id, redis_client=redis_client # NOVO: Passa o cliente Redis
        )
        # Se a câmera for criada como ativa, envia comando para iniciar o processamento
        if new_camera.is_active:
            messaging.publish_camera_command(action="start", camera=new_camera)

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

@router.get("/{camera_id}/thumbnail",
            tags=["Câmeras"],
            response_class=Response,
            responses={
                200: {"content": {"image/jpeg": {}}},
                404: {"description": "Câmera não encontrada ou stream indisponível"}
            })
async def get_camera_thumbnail(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_query_token) # Usa a nova dependência
):
    """
    Captura um único frame de uma câmera e o retorna como uma imagem JPEG.
    """
    camera = await crud.get_camera_by_id(db, camera_id=camera_id)
    if not camera or camera.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")

    if not camera.is_active:
        raise HTTPException(status_code=400, detail="A câmera está inativa")

    # Tenta capturar o frame de forma assíncrona para não bloquear o servidor
    def capture_frame():
        cap = cv2.VideoCapture(camera.rtsp_url)
        if not cap.isOpened():
            return None, None
        
        # Tenta ler alguns frames para garantir que a imagem não seja preta/cinza do início da conexão
        for _ in range(5):
            success, frame = cap.read()
            if success:
                break
        
        cap.release()
        return success, frame

    loop = asyncio.get_running_loop()
    success, frame = await loop.run_in_executor(None, capture_frame)

    if not success or frame is None:
        raise HTTPException(status_code=404, detail="Não foi possível capturar a imagem do stream da câmera")

    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    return Response(content=buffer.tobytes(), media_type="image/jpeg")

@router.patch("/{camera_id}", response_model=schemas.Camera)
async def update_camera(
    camera_id: int,
    camera_update: schemas.CameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client),
):
    """Atualiza uma câmera e envia comandos de start/stop se o status de ativação mudar."""
    camera_before_update = await crud.get_camera_by_id(db, camera_id=camera_id)
    if not camera_before_update or camera_before_update.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")

    updated_camera = await crud.update_camera(
        db=db,
        camera_id=camera_id,
        camera_update=camera_update,
        client_id=current_user.client_id,
        redis_client=redis_client
    )

    # Verifica se o status 'is_active' mudou
    if camera_update.is_active is not None and camera_before_update.is_active != updated_camera.is_active:
        if updated_camera.is_active:
            # A câmera foi ativada
            messaging.publish_camera_command(action="start", camera=updated_camera)
        else:
            # A câmera foi desativada
            messaging.publish_camera_command(action="stop", camera=updated_camera)

    # Se a URL RTSP mudou, precisamos parar o antigo e iniciar o novo
    if camera_update.rtsp_url and camera_before_update.rtsp_url != updated_camera.rtsp_url:
        messaging.publish_camera_command(action="stop", camera=camera_before_update)
        messaging.publish_camera_command(action="start", camera=updated_camera)

    return updated_camera

@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client), # NOVO: Adiciona o cliente Redis
):
    """Apaga uma câmera e invalida o cache de estatísticas."""
    camera_to_delete = await crud.get_camera_by_id(db, camera_id=camera_id)
    if not camera_to_delete or camera_to_delete.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")

    # Envia comando para parar o processamento antes de apagar
    messaging.publish_camera_command(action="stop", camera=camera_to_delete)

    await crud.delete_camera(db, camera_id=camera_id, client_id=current_user.client_id, redis_client=redis_client) # NOVO: Passa o cliente Redis e client_id
    return None
