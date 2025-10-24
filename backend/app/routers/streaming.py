import asyncio
import cv2
import logging # Adicionado para melhor logging
import httpx # Adicionado para fazer chamadas de API assíncronas
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, Query, HTTPException
from starlette.websockets import WebSocketState
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from ..dependencies import get_db
from .. import crud, models
from ..config import settings
from ..schemas import TokenData

router = APIRouter(
    prefix="/streaming",
    tags=["Streaming"],
)

MEDIA_SERVER_API_URL = "http://gt-vision-media-server:9997/v3"

@router.post("/start/{camera_id}", status_code=status.HTTP_200_OK)
async def start_stream_proxy(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    # Esta rota pode ser chamada internamente, então não requer um utilizador logado,
    # mas em produção, poderia ser protegida por uma chave de API interna.
):
    """
    Instrui o MediaMTX a começar a puxar o stream RTSP de uma câmera.
    Isso torna o stream disponível em rtsp://gt-vision-media-server:8554/{camera_id}.
    Esta rota é idempotente: se o stream já existir, não faz nada.
    """
    camera = await crud.get_camera_by_id(db, camera_id=camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Câmera não encontrada")

    path_name = str(camera.id)
    add_path_url = f"{MEDIA_SERVER_API_URL}/config/paths/add/{path_name}"
    
    payload = {
        "source": camera.rtsp_url, # A URL original da câmera
        "sourceOnDemand": False,   # CORRIGIDO: Queremos que o stream seja puxado continuamente
        "runOnDemand": "",         # Garante que não há comandos de execução sob demanda
        "runOnDemandRestart": False
    }

    # Configura a autenticação se as credenciais estiverem definidas
    auth = None
    if settings.MEDIA_SERVER_API_USER and settings.MEDIA_SERVER_API_PASS:
        auth = (settings.MEDIA_SERVER_API_USER, settings.MEDIA_SERVER_API_PASS)

    async with httpx.AsyncClient() as client:
        try:
            # Usamos POST para adicionar/atualizar a configuração do path
            response = await client.post(add_path_url, json=payload, auth=auth)
            response.raise_for_status() # Lança uma exceção para códigos de erro HTTP
            logging.info(f"Proxy para a câmera {camera_id} ({camera.name}) configurado no MediaMTX.")
            return {"message": f"Proxy para a câmera {camera_id} ativado com sucesso."}
        except httpx.HTTPStatusError as e:
            # Se o path já existe, a API do MediaMTX pode retornar um erro.
            if e.response.status_code == 401:
                logging.error("Erro de autenticação com a API do MediaMTX. Verifique as variáveis MEDIA_SERVER_API_USER e MEDIA_SERVER_API_PASS.")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro de configuração interna do servidor de streaming.")
            logging.error(f"Erro ao configurar o proxy no MediaMTX para a câmera {camera_id}: {e.response.text}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Falha ao comunicar com o media server.")
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão ao tentar configurar o proxy no MediaMTX: {e}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Não foi possível conectar ao media server.")

async def get_current_user_from_token(token: str, db: AsyncSession) -> models.User:
    """Valida o token JWT e retorna o utilizador."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
    except JWTError:
        return None
    
    user = await crud.get_user_by_email(db, email=token_data.email)
    return user

@router.websocket("/ws/player/{camera_id}")
async def websocket_player_setup(websocket: WebSocket, camera_id: int, token: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    Endpoint WebSocket para configurar o player do frontend.
    1. Autentica o usuário.
    2. Garante que o stream da câmera está ativo no MediaMTX.
    3. Envia a URL WebRTC para o frontend se conectar diretamente ao MediaMTX.
    """
    await websocket.accept()

    user = await get_current_user_from_token(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
        return

    camera = await crud.get_camera_by_id(db, camera_id=camera_id)
    # Adicionada verificação de permissão de admin para acessar câmeras de outros clientes
    is_admin = user.role == models.UserRole.ADMIN
    if not camera or (not is_admin and camera.client_id != user.client_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Camera not found or access denied")
        return

    if not camera.is_active:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Camera is inactive")
        return

    try:
        # 1. Garante que o proxy está ativo no MediaMTX
        await start_stream_proxy(camera_id, db)
        
        # --- CORREÇÃO APLICADA AQUI ---
        # 2. Envia a URL WebRTC para o frontend usando o host público configurado
        # O frontend acessará o MediaMTX através do endereço exposto pelo Docker.
        webrtc_url = f"http://{settings.MEDIA_SERVER_PUBLIC_HOST}:8889/{camera.id}/webrtc"
        # ---------------------------------
        await websocket.send_json({"type": "webrtc_url", "url": webrtc_url})
        logging.info(f"URL WebRTC {webrtc_url} enviada para o frontend para a câmera {camera_id}")

    except Exception as e:
        logging.error(f"Erro inesperado no streaming da câmara {camera_id}: {e}")
        # Apenas fecha a conexão aqui, o finally não é mais necessário para isso.
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason=str(e))
    finally:
        # Garante que a desconexão seja logada, mas não tenta fechar novamente.
        logging.info(f"Conexão WebSocket para a câmera {camera_id} encerrada.")