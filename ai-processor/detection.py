import cv2
import time
import logging # Usar a biblioteca padrão de logging
from ultralytics import YOLO
# CORREÇÃO 1: O nome da classe foi atualizado para LicensePlateRecognizer
from fast_plate_ocr import LicensePlateRecognizer 
from api_client import APIClient

# Configurar o logger padrão
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar modelos (fora da função para carregar apenas uma vez)
vehicle_detector = YOLO("yolov8n.pt")
# CORREÇÃO 2: A forma de inicializar a classe mudou.
plate_recognizer = LicensePlateRecognizer(hub_ocr_model="global-plates-mobile-vit-v2-model")

def process_camera_stream(camera: dict, api_client: APIClient):
    """
    Processa o stream de vídeo de uma câmera para detecção de veículos e placas.
    """
    rtsp_url = camera.get("rtsp_url")
    camera_id = camera.get("id")

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        logging.error(f"Não foi possível abrir o stream da câmera {camera_id}: {rtsp_url}")
        return

    logging.info(f"Iniciando processamento para a câmera {camera_id}...")

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error(f"Não foi possível ler o frame da câmera {camera_id}. A tentar reconectar...")
            cap.release()
            time.sleep(5)
            cap = cv2.VideoCapture(rtsp_url)
            continue

        vehicle_results = vehicle_detector(frame)[0]

        for result in vehicle_results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result

            if score > 0.5 and vehicle_detector.names[int(class_id)] in ['car', 'truck', 'bus']:
                vehicle_roi = frame[int(y1):int(y2), int(x1):int(x2)]

                try:
                    plate_results = plate_recognizer(image=vehicle_roi)

                    if plate_results:
                        for plate_result in plate_results:
                            license_plate = plate_result["text"]
                            logging.info(f"Placa detectada pela câmera {camera_id}: {license_plate}")

                            # Certifique-se que a pasta 'captures' existe
                            image_filename = f"captures/plate_{camera_id}_{license_plate}_{int(time.time())}.jpg"
                            cv2.imwrite(image_filename, vehicle_roi)

                            sighting_data = {
                                "license_plate": license_plate,
                                "image_filename": image_filename,
                                "camera_id": camera_id
                            }
                            api_client.create_sighting(sighting_data)
                except Exception as e:
                    logging.error(f"Ocorreu um erro no reconhecimento de placa: {e}")

    cap.release()