import asyncio
import cv2
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from ..dependencies import get_db
from .. import crud, models
from ..config import settings
from ..schemas import TokenData

router = APIRouter(
    prefix="/ws",
    tags=["Streaming"],
)

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

@router.websocket("/stream/{camera_id}")
async def websocket_stream(
    websocket: WebSocket,
    camera_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint WebSocket para transmitir vídeo de uma câmara em tempo real.
    """
    user = await get_current_user_from_token(token, db)
    if not user:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
        return

    camera = await crud.get_camera_by_id(db, camera_id=camera_id)
    if not camera or camera.client_id != user.client_id:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Camera not found or access denied")
        return
    
    if not camera.is_active:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Camera is inactive")
        return

    await websocket.accept()
    
    cap = cv2.VideoCapture(camera.rtsp_url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Could not open video stream")
        return

    try:
        while True:
            success, frame = cap.read()
            if not success:
                await asyncio.sleep(1)
                cap.release()
                cap = cv2.VideoCapture(camera.rtsp_url)
                if not cap.isOpened():
                    break
                continue

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                continue
            
            await websocket.send_bytes(buffer.tobytes())
            await asyncio.sleep(1/30) # ~30 FPS

    except WebSocketDisconnect:
        print(f"Cliente desconectado da câmara {camera_id}")
    except Exception as e:
        print(f"Erro no streaming da câmara {camera_id}: {e}")
    finally:
        cap.release()
        if websocket.client_state.value != 3:
             await websocket.close()