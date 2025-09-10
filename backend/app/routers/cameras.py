from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse
import cv2
import asyncio

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

# --- NOVA ROTA DE STREAMING DE VÍDEO ---

async def generate_frames(rtsp_url: str):
    """
    Gerador que captura frames da câmera, codifica para JPEG e envia.
    Tenta reconectar-se se o stream cair.
    """
    while True:
        # Usamos a API do FFMPEG para maior compatibilidade com RTSP
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            print(f"Erro ao abrir o stream: {rtsp_url}. Tentando novamente em 5s.")
            await asyncio.sleep(5)
            continue

        print(f"Stream conectado com sucesso: {rtsp_url}")
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"Frame perdido. Reconectando ao stream: {rtsp_url}")
                break

            # Codifica o frame para JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            # Envia o frame no formato multipart/x-mixed-replace
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Controla o FPS para ~30
            await asyncio.sleep(1/30)
        
        cap.release()
        await asyncio.sleep(5)


@router.get("/{camera_id}/stream", summary="Obtém o stream de vídeo ao vivo de uma câmera")
async def stream_camera(
    camera_id: int,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    """
    Endpoint que retorna um stream de vídeo no formato MJPEG.
    Pode ser usado diretamente no `src` de uma tag `<img>` no frontend.
    """
    db_camera = await crud.get_camera_by_id(db, camera_id=camera_id)
    
    if not db_camera or db_camera.client_id != current_user.client_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Câmera não encontrada")

    # Usa o campo rtsp_url que você já tem no seu modelo
    return StreamingResponse(
        generate_frames(db_camera.rtsp_url),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )