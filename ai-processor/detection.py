import cv2
import os
import logging
from ultralytics import YOLO
from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer # Nome da classe corrigido
import numpy as np

class PlateDetector:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
        # Instanciação corrigida, utilizando um modelo padrão do hub
        self.plate_recognizer = LicensePlateRecognizer(hub_ocr_model="cct-xs-v1-global-model")
        self.logger = logging.getLogger(__name__)
        self.captures_dir = "/app/captures"
        os.makedirs(self.captures_dir, exist_ok=True)

    def detect_and_recognize(self, frame: np.ndarray, camera_id: int) -> list:
        detections = []
        # As classes para 'license_plate' na COCO são geralmente a 2 ou 7
        results = self.model(frame, classes=[2, 7], conf=0.5, verbose=False)

        plate_crops = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                crop = frame[y1:y2, x1:x2]
                plate_crops.append(crop)
        
        if not plate_crops:
            return detections

        try:
            # O método de reconhecimento se chama 'run'
            # Ele retorna uma lista de strings diretamente
            recognized_plates_text = self.plate_recognizer.run(plate_crops)
            
            for i, plate_text in enumerate(recognized_plates_text):
                if plate_text:
                    image_filename = f"capture_{camera_id}_{plate_text}_{cv2.getTickCount()}.jpg"
                    image_path = os.path.join(self.captures_dir, image_filename)
                    cv2.imwrite(image_path, plate_crops[i])
                    detections.append({
                        "plate": plate_text,
                        "image_path": image_path
                    })
        except Exception as e:
            self.logger.error(f"Erro ao reconhecer matrículas: {e}")

        return detections