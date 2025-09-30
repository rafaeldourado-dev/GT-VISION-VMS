from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import redis.asyncio as redis
from onvif import ONVIFCamera
import logging # Boa prática adicionar logging

from ..dependencies import get_db, get_current_user, get_redis_client
from .. import crud, models, schemas

router = APIRouter(
    prefix="/cameras",
    tags=["Câmeras"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

# --- ROTA CORRIGIDA PARA ADIÇÃO MANUAL (RESOLVE O ERRO 422) ---
@router.post("/", response_model=schemas.Camera, status_code=status.HTTP_201_CREATED)
async def create_camera_manual(
    camera: schemas.CameraCreate, # <<< USA O SCHEMA ANTIGO/CORRETO PARA O FORMULÁRIO
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client),
):
    """
    Cria uma nova câmera fornecendo manualmente a URL RTSP.
    Esta rota corresponde ao formulário da interface web.
    """
    try:
        new_camera = await crud.create_client_camera(
            db=db, camera=camera, client_id=current_user.client_id, redis_client=redis_client
        )
        return new_camera
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uma câmera com esta URL RTSP já existe no banco de dados.",
        )

# --- FUNÇÃO AUXILIAR ONVIF (MELHORADA COM LOGGING E ROBUSTEZ) ---
async def discover_rtsp_url(ip: str, port: int, user: str, pwd: str) -> str | None:
    """
    Tenta se conectar a uma câmera via ONVIF para descobrir seu RTSP URL.
    Retorna o URL ou None se falhar.
    """
    try:
        mycam = ONVIFCamera(ip, port, user, pwd)
        await mycam.update_xaddrs()
        media_service = mycam.create_media_service()
        
        profiles = await media_service.GetProfiles()
        # Garante que a câmera retornou perfis
        if not profiles:
            logging.warning(f"Nenhum perfil ONVIF encontrado para a câmera em {ip}:{port}.")
            return None

        token = profiles[0].token
        
        uri_info = await media_service.GetStreamUri({
            'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}},
            'ProfileToken': token
        })
        
        return uri_info.Uri
    except Exception as e:
        # Loga o erro real para facilitar o debug futuro
        logging.error(f"Falha na descoberta ONVIF para {ip}:{port}. Erro: {e}")
        return None

# --- NOVA ROTA PARA DESCOBERTA ONVIF (MANTÉM A FUNCIONALIDADE) ---
@router.post("/discover/", response_model=schemas.Camera, status_code=status.HTTP_201_CREATED)
async def create_camera_onvif(
    camera: schemas.CameraCreateOnvif, # Usa o schema de descoberta
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client),
):
    """
    Cria uma nova câmera via descoberta ONVIF.
    O sistema tentará descobrir o RTSP URL automaticamente.
    """
    rtsp_url = await discover_rtsp_url(
        ip=camera.ip_address,
        port=camera.port,
        user=camera.username,
        pwd=camera.password,
    )

    if not rtsp_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível descobrir o RTSP URL via ONVIF. Verifique os dados da câmera ou se ela suporta ONVIF."
        )

    # Cria o objeto final com o URL descoberto para salvar no banco
    camera_to_create = schemas.CameraCreate(
        name=camera.name,
        rtsp_url=rtsp_url,
        is_active=camera.is_active,
        latitude=camera.latitude,
        longitude=camera.longitude
    )

    try:
        new_camera = await crud.create_client_camera(
            db=db, camera=camera_to_create, client_id=current_user.client_id, redis_client=redis_client
        )
        return new_camera
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uma câmera com esta URL RTSP já existe no banco de dados.",
        )

# --- ROTAS EXISTENTES (sem alterações) ---
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
    redis_client: redis.Redis = Depends(get_redis_client),
):
    """Apaga uma câmera e invalida o cache de estatísticas."""
    camera_to_delete = await crud.get_camera_by_id(db, camera_id=camera_id)
    if not camera_to_delete or camera_to_delete.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")
    
    # Movendo o commit para dentro da função CRUD para melhor encapsulamento
    await crud.delete_camera(db, camera_id=camera_id, client_id=current_user.client_id, redis_client=redis_client)
    
    return None