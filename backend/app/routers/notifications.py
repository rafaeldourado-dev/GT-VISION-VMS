import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from ..dependencies import get_db, get_redis_client
from .. import models
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/ws",
    tags=["Notifications"],
)

logger = logging.getLogger(__name__)

@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Endpoint WebSocket para receber notificações em tempo real (ex: alertas de lista negra).
    """
    await websocket.accept()
    
    try:
        # Valida o token e obtém o usuário.
        # Este bloco lida com tokens inválidos ou expirados sem lançar uma HTTPException.
        user = await get_current_user(db=db, token=token)
        if not user:
            raise ValueError("User not found")
    except Exception:
        # Se a validação falhar por qualquer motivo (token expirado, inválido, etc.),
        # fecha a conexão de forma limpa.
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
        return

    channel_name = f"alerts:{user.client_id}"
    pubsub = redis_client.pubsub()
    
    try:
        await pubsub.subscribe(channel_name)
        logger.info(f"Usuário {user.email} inscrito no canal de alertas: {channel_name}")
        
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=None)
            if message and message["type"] == "message":
                logger.info(f"Enviando notificação para o usuário {user.email}: {message['data']}")
                await websocket.send_text(message['data'])

    except WebSocketDisconnect:
        logger.info(f"Cliente {user.email} desconectado do canal de alertas.")
    except Exception as e:
        logger.error(f"Erro no WebSocket de notificações para {user.email}: {e}")
    finally:
        await pubsub.unsubscribe(channel_name)
        logger.info(f"Usuário {user.email} desinscrito do canal {channel_name}.")