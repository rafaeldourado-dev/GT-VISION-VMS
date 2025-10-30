import cv2
import logging
import os
from sqlalchemy.orm import Session
from app import models, crud
from app.database import SessionLocal
from typing import Optional

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _generate_thumbnail(camera: models.Camera) -> Optional[str]:
    """
    Tenta capturar um frame da câmera e salvar como thumbnail.
    Retorna o URL do thumbnail em caso de sucesso.
    """
    try:
        # Tenta abrir o stream RTSP
        cap = cv2.VideoCapture(camera.rtsp_url)
        if not cap.isOpened():
            logger.error(f"Cannot open RTSP stream for camera {camera.id}: {camera.rtsp_url}")
            return None
        
        # Lê um único frame
        ret, frame = cap.read()
        cap.release()

        if ret:
            thumbnail_dir = "static/thumbnails"
            # Garante que o diretório existe (apesar de já o termos criado no main.py)
            os.makedirs(thumbnail_dir, exist_ok=True) 
            
            thumbnail_path = f"{thumbnail_dir}/{camera.id}.jpg"
            
            # Salva o frame como JPEG com qualidade 85
            cv2.imwrite(thumbnail_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            logger.info(f"Generated thumbnail for camera {camera.id} at {thumbnail_path}")
            # Retorna o caminho do URL que o frontend pode usar
            return f"/{thumbnail_path}"
        else:
            logger.warning(f"Could not read frame from camera {camera.id}")
            return None
    except Exception as e:
        logger.error(f"Error generating thumbnail for camera {camera.id}: {e}")
        return None

def generate_thumbnail_task(camera_id: int):
    """
    Task de background para gerar e salvar o thumbnail.
    """
    logger.info(f"Starting thumbnail task for camera {camera_id}")
    db: Session = SessionLocal()
    try:
        # Pega a câmera do banco de dados usando uma nova sessão
        camera = crud.get_camera(db, camera_id=camera_id)
        if not camera:
            logger.error(f"Camera {camera_id} not found for thumbnail generation.")
            return

        # Gera o thumbnail
        thumbnail_url = _generate_thumbnail(camera)
        
        if thumbnail_url:
            # Atualiza o modelo da câmera com o novo URL
            camera.thumbnail_url = thumbnail_url
            db.add(camera)
            db.commit()
            logger.info(f"Updated thumbnail URL for camera {camera.id}")
    except Exception as e:
        logger.error(f"Failed thumbnail task for camera {camera_id}: {e}")
    finally:
        db.close()