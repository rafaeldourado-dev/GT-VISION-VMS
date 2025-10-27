import asyncio
import cv2
import logging # Adicionado para melhor logging
import os # NOVO: Importa o módulo 'os'
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from starlette.websockets import WebSocketState # Import needed for WebSocketState.CONNECTED

from ..dependencies import get_db
from .. import crud, models
from ..config import settings
from ..schemas import TokenData

router = APIRouter(
    prefix="/ws",  # <-- Correct prefix for the old method
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
        logging.warning("JWTError decoding token during WebSocket auth.") # Added log
        return None
    
    user = await crud.get_user_by_email(db, email=token_data.email)
    return user

@router.websocket("/stream/{camera_id}") # <-- Correct path for the old method
async def websocket_stream(
    websocket: WebSocket,
    camera_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint WebSocket para transmitir vídeo de uma câmara em tempo real (via OpenCV/JPEG).
    """
    await websocket.accept() # Accept connection first to send close reasons

    user = await get_current_user_from_token(token, db)
    if not user:
        logging.warning(f"WebSocket connection rejected for camera {camera_id}: Invalid token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
        return

    camera = await crud.get_camera_by_id(db, camera_id=camera_id)

    # --- Verificação de Permissão (Simplificada) ---
    # Adapte se precisar de lógica de admin separada
    if not camera or camera.client_id != user.client_id:
        logging.warning(f"WebSocket connection rejected for camera {camera_id}: Camera not found or access denied for user {user.email}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Camera not found or access denied")
        return
    # --- FIM DA Verificação ---
    
    if not camera.is_active:
        logging.warning(f"WebSocket connection rejected for camera {camera_id}: Camera is inactive")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Camera is inactive")
        return

    # User is authenticated and camera is valid/active
    logging.info(f"User {user.email} authenticated. Initiating OpenCV stream for camera {camera_id} ({camera.name}) at {camera.rtsp_url}")
    
    cap = None # Initialize cap to None
    try:
        # Use environment variable for RTSP transport protocol if needed
        # Often helps with connection issues
        env_options = {}
        if os.environ.get('OPENCV_FFMPEG_CAPTURE_OPTIONS') == 'rtsp_transport;tcp':
            env_options = {'CAP_PROP_OPEN_TIMEOUT_MSEC': 5000, 'CAP_PROP_READ_TIMEOUT_MSEC': 5000}
            logging.info(f"Using RTSP transport TCP for camera {camera_id}")
            cap = cv2.VideoCapture(camera.rtsp_url, cv2.CAP_FFMPEG, params=env_options)
        else:
            cap = cv2.VideoCapture(camera.rtsp_url, cv2.CAP_FFMPEG)


        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # Setting resolution might fail
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not cap.isOpened():
            logging.error(f"Could not open RTSP stream for camera {camera_id}: {camera.rtsp_url}")
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Could not open video stream")
            return

        while True:
            if websocket.client_state != WebSocketState.CONNECTED:
                logging.info(f"WebSocket disconnected by client for camera {camera_id}. Stopping stream loop.")
                break

            success, frame = cap.read()
            if not success:
                logging.warning(f"Failed to read frame from camera {camera_id}. Attempting reconnect...")
                await asyncio.sleep(5) # Increased wait time before reconnect
                cap.release()
                if os.environ.get('OPENCV_FFMPEG_CAPTURE_OPTIONS') == 'rtsp_transport;tcp':
                     cap = cv2.VideoCapture(camera.rtsp_url, cv2.CAP_FFMPEG, params=env_options)
                else:
                    cap = cv2.VideoCapture(camera.rtsp_url, cv2.CAP_FFMPEG)
                
                if not cap.isOpened():
                    logging.error(f"Could not reopen stream for camera {camera_id} after failure. Closing connection.")
                    await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Stream permanently lost")
                    break # Exit loop if reconnect fails
                logging.info(f"Successfully reconnected to camera {camera_id}.")
                continue # Go back to reading the next frame

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80]) # JPEG quality 80
            if not ret:
                logging.warning(f"Failed to encode JPEG frame for camera {camera_id}")
                continue
            
            # Send the frame bytes
            await websocket.send_bytes(buffer.tobytes())
            await asyncio.sleep(1/30) # ~30 FPS frame rate control

    except WebSocketDisconnect:
        logging.info(f"WebSocket client disconnected explicitly for camera {camera_id}")
    except asyncio.CancelledError:
         logging.info(f"Streaming task cancelled for camera {camera_id}")
    except Exception as e:
        logging.exception(f"Unexpected error during OpenCV streaming for camera {camera_id}: {e}") # Use logging.exception to include traceback
        if websocket.client_state == WebSocketState.CONNECTED:
             await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason=f"Streaming error: {e}")
    finally:
        logging.info(f"Cleaning up OpenCV stream resources for camera {camera_id}")
        if cap and cap.isOpened():
            cap.release()
        # Ensure WebSocket is closed if it wasn't already
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
            except RuntimeError as e:
                if 'Cannot call "send" once a close message has been sent' in str(e):
                    logging.debug(f"Ignoring close error for camera {camera_id}: WebSocket already closed.")
                else:
                    logging.exception(f"RuntimeError while closing WebSocket for camera {camera_id}: {e}")
            except Exception as e:
                 logging.exception(f"Unexpected error closing WebSocket for camera {camera_id}: {e}")
        logging.info(f"Stream handler for camera {camera_id} finished.")