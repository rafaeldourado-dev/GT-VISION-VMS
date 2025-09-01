import cv2
import easyocr
import re
import logging
from ultralytics import YOLO
import torch

logger = logging.getLogger(__name__)

class LPRProcessor:
    def __init__(self):
        device = 'cpu' # Força o uso de CPU
        logger.info(f"A carregar modelos de IA no dispositivo: {device.upper()}")
        
        try:
            # Coloque o seu melhor modelo de deteção de matrículas aqui
            self.plate_detector = YOLO('models_ai/best.pt').to(device)
            logger.info("Modelo de deteção de matrículas carregado com sucesso.")
        except Exception as e:
            logger.error(f"Falha ao carregar o modelo de matrículas: {e}. A usar modelo genérico.")
            self.plate_detector = YOLO('yolov8n.pt').to(device)
        
        self.ocr_reader = easyocr.Reader(['pt'], gpu=False) # Força o uso de CPU
        logger.info("Modelo EasyOCR (OCR) carregado.")

    def _clean_plate_text(self, text: str) -> str:
        """Limpa e valida o texto da matrícula."""
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        if len(cleaned) >= 5 and len(cleaned) <= 8: # Aumentado para 8 para placas Mercosul
            return cleaned
        return ""

    def process_frame(self, frame, camera_id: int):
        """Processa um frame, deteta matrículas e extrai o texto."""
        if frame is None: return None

        # A classe 0 é geralmente 'license-plate' num modelo customizado
        results = self.plate_detector(frame, verbose=False, conf=0.6)

        for result in results:
            if len(result.boxes) > 0:
                box = result.boxes[0] # Pega a deteção com maior confiança
                coords = box.xyxy[0].cpu().numpy().astype(int)
                confidence = float(box.conf[0])
                
                x1, y1, x2, y2 = coords
                plate_image = frame[y1:y2, x1:x2]

                if plate_image.size == 0: continue

                ocr_result = self.ocr_reader.readtext(plate_image, detail=0, paragraph=True)

                if ocr_result:
                    plate_number = self._clean_plate_text("".join(ocr_result))
                    if plate_number:
                        logger.info(f"CÂMARA {camera_id}: Matrícula detetada '{plate_number}'")
                        return {
                            "license_plate": plate_number,
                            "confidence": confidence,
                            "camera_id": camera_id,
                        }
        return None