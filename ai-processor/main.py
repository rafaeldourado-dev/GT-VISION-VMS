import logging
import time
import os
import uuid
from threading import Thread
import cv2

# Novas importações
from api_client import APIClient
from detection import PlateDetector

# --- CONFIGURAÇÃO ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
API_BASE_URL = "http://gt-vision-backend:8000"

# --- SEÇÃO DE COLETA DE DADOS PARA TREINAMENTO CONTÍNUO ---
PENDING_TRAINING_DIR = "pending_training"
# Garante que o diretório para salvar os dados de treino exista
os.makedirs(PENDING_TRAINING_DIR, exist_ok=True)

def salvar_para_treinamento(frame_completo, texto_da_placa):
    """
    Salva o frame completo do vídeo e a placa lida para o próximo ciclo de treinamento.
    """
    try:
        # Garante que a placa não está vazia antes de salvar
        if not texto_da_placa or not texto_da_placa.strip():
            return

        # Gera um nome de arquivo base único para evitar colisões
        unique_id = str(uuid.uuid4())
        nome_arquivo_imagem = f"{unique_id}.jpg"
        caminho_imagem = os.path.join(PENDING_TRAINING_DIR, nome_arquivo_imagem)

        # Salva a imagem (o frame completo do vídeo)
        cv2.imwrite(caminho_imagem, frame_completo)

        # Salva as informações da placa em um arquivo de texto correspondente
        caminho_info = os.path.join(PENDING_TRAINING_DIR, f"{unique_id}.txt")
        with open(caminho_info, "w") as f:
            f.write(f"{nome_arquivo_imagem},{texto_da_placa}")
        
        logging.info(f"Dados salvos para futuro treinamento: Placa {texto_da_placa}")

    except Exception as e:
        logging.error(f"Erro ao salvar dados para treinamento: {e}")

# --- FIM DA SEÇÃO DE COLETA DE DADOS ---


def process_camera_stream(camera_info: dict, detector: PlateDetector, api_client: APIClient):
    rtsp_url = camera_info.get("rtsp_url")
    camera_id = camera_info.get("id")
    camera_name = camera_info.get("name", f"Câmera {camera_id}")
    
    logging.info(f"Iniciando processamento para a câmera: {camera_name} ({rtsp_url})")
    
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        logging.error(f"Não foi possível abrir o stream de vídeo para a câmera {camera_name}.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.warning(f"Stream da câmera {camera_name} terminou. Tentando reconectar em 10 segundos.")
            cap.release()
            time.sleep(10)
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                logging.error(f"Falha ao reconectar à câmera {camera_name}. Encerrando thread.")
                break
            continue

        try:
            # A função de detecção agora opera sobre o frame capturado
            detections = detector.detect_and_recognize(frame, camera_id)
            for detection in detections:
                plate_text = detection.get("plate")
                image_path = detection.get("image_path")
                
                if plate_text and image_path:
                    logging.info(f"Placa detectada pela câmera {camera_name}: {plate_text}")
                    # Envia o resultado para a API
                    api_client.send_sighting_to_api(
                        plate=plate_text,
                        image_filename=image_path,
                        camera_id=camera_id
                    )
                    
                    # <<< NOVA FUNCIONALIDADE AQUI >>>
                    # Salva o frame completo e a placa para o nosso dataset de treinamento
                    salvar_para_treinamento(frame, plate_text)

        except Exception as e:
            logging.error(f"Erro durante o processamento do frame da câmera {camera_name}: {e}")

    cap.release()
    logging.info(f"Processamento para a câmera {camera_name} encerrado.")

def main():
    logging.info("Iniciando o serviço AI-Processor...")
    
    api_client = APIClient(base_url=API_BASE_URL)
    plate_detector = PlateDetector(model_path="yolov8n.pt")

    while not api_client.check_api_health():
        logging.info("Aguardando a API do backend... tentando novamente em 5 segundos.")
        time.sleep(5)
        
    logging.info("Backend API está disponível. Buscando câmaras...")
    
    cameras = api_client.get_cameras_from_api()

    if not cameras:
        logging.warning("Nenhuma câmera encontrada para processar. O serviço vai terminar.")
        return

    threads = []
    for camera in cameras:
        if camera.get("is_active"):
            thread = Thread(target=process_camera_stream, args=(camera, plate_detector, api_client))
            threads.append(thread)
            thread.start()
        else:
            logging.info(f"Câmera '{camera.get('name')}' está inativa e não será processada.")

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()