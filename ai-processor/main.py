import logging
import time
import os
import uuid
from threading import Thread
import cv2
from flask import Flask, request, jsonify
import json # <--- ADICIONADO para manipulação de JSON

# --- Módulos do projeto ---
from alert_system import logs, alarmes, onoff_suporte
from database import database, crud
from sqlalchemy.orm import Session
from api_client import APIClient
from detection import PlateDetector

# --- CONFIGURAÇÃO ---
API_BASE_URL = "http://gt-vision-backend:8000"
PENDING_TRAINING_DIR = "pending_training"
RECEIVED_WEBHOOKS_DIR = "received_webhooks" # <--- ADICIONADO: Pasta para guardar os JSONs
os.makedirs(PENDING_TRAINING_DIR, exist_ok=True)
os.makedirs(RECEIVED_WEBHOOKS_DIR, exist_ok=True) # <--- ADICIONADO: Cria a pasta


def salvar_para_treinamento(frame_completo, texto_da_placa):
    """
    Salva o frame completo do vídeo e a placa lida para o próximo ciclo de treinamento.
    """
    try:
        if not texto_da_placa or not texto_da_placa.strip():
            return
        unique_id = str(uuid.uuid4())
        nome_arquivo_imagem = f"{unique_id}.jpg"
        caminho_imagem = os.path.join(PENDING_TRAINING_DIR, nome_arquivo_imagem)
        cv2.imwrite(caminho_imagem, frame_completo)
        caminho_info = os.path.join(PENDING_TRAINING_DIR, f"{unique_id}.txt")
        with open(caminho_info, "w") as f:
            f.write(f"{nome_arquivo_imagem},{texto_da_placa}")
        logging.info(f"Dados salvos para futuro treinamento: Placa {texto_da_placa}")
    except Exception as e:
        logging.error(f"Erro ao salvar dados para treinamento: {e}")


def process_camera_stream(camera_info: dict, detector: PlateDetector, api_client: APIClient, db_session: Session):
    """
    Função de processamento de vídeo para câmaras via RTSP (lógica original).
    """
    rtsp_url = camera_info.get("rtsp_url")
    camera_id = camera_info.get("id")
    camera_name = camera_info.get("name", f"Câmera {camera_id}")

    logging.info(f"Iniciando processamento RTSP para a câmera: {camera_name} ({rtsp_url})")

    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        logging.error(f"Não foi possível abrir o stream de vídeo para a câmera {camera_name}.")
        return

    while camera_info.get('thread_active', True):
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
            detections = detector.detect_and_recognize(frame, camera_id)
            for detection in detections:
                plate_text = detection.get("plate")
                image_path = detection.get("image_path")

                if plate_text and image_path:
                    logging.info(f"Placa detectada (RTSP) pela câmera {camera_name}: {plate_text}")

                    api_client.send_sighting_to_api(
                        plate=plate_text,
                        image_filename=image_path,
                        camera_id=camera_id
                    )
                    salvar_para_treinamento(frame, plate_text)
                    crud.get_or_create_vehicle(db=db_session, plate=plate_text)
                    logging.info(f"Placa '{plate_text}' (RTSP) registrada no banco de dados local.")

        except Exception as e:
            logging.error(f"Erro durante o processamento do frame da câmera {camera_name}: {e}")

        time.sleep(0.01)

    cap.release()
    logging.info(f"Processamento RTSP para a câmera {camera_name} encerrado.")


def process_lpr_webhook(data: dict, api_client: APIClient, db_session: Session):
    """
    Processa os dados de LPR recebidos de um webhook e GUARDA O JSON num ficheiro.
    """
    try:
        # --- NOVO CÓDIGO PARA GUARDAR O JSON ---
        try:
            plate_for_filename = data.get("Plate", {}).get("PlateNumber", "UNKNOWN_PLATE")
            timestamp = int(time.time())
            # Cria um nome de ficheiro único para cada deteção
            nome_ficheiro = f"{timestamp}_{plate_for_filename}.json"
            caminho_ficheiro = os.path.join(RECEIVED_WEBHOOKS_DIR, nome_ficheiro)

            # Guarda o dicionário 'data' como um ficheiro JSON formatado
            with open(caminho_ficheiro, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logging.info(f"Dados do webhook guardados com sucesso em: {caminho_ficheiro}")
        except Exception as e:
            logging.error(f"Falha ao tentar guardar o ficheiro JSON do webhook: {e}")
        # --- FIM DO NOVO CÓDIGO ---

        plate_text = data.get("Plate", {}).get("PlateNumber")
        camera_id = data.get("Channel")
        camera_name = data.get("DeviceName", f"Câmera LPR {camera_id}")

        if not plate_text:
            logging.warning("Webhook LPR recebido sem o número da placa. Dados: %s", data)
            return

        logging.info(f"Placa recebida via Webhook da câmera {camera_name}: {plate_text}")

        api_client.send_sighting_to_api(
            plate=plate_text,
            image_filename=None,
            camera_id=camera_id
        )
        crud.get_or_create_vehicle(db=db_session, plate=plate_text)
        logging.info(f"Placa '{plate_text}' (Webhook) registrada no banco de dados local.")

    except Exception as e:
        logging.error(f"Erro ao processar o webhook da câmara {camera_name}: {e}")


def main():
    """
    Função principal que gere os processamentos RTSP e o servidor de webhook.
    """
    logs.configurar_logging()
    database.init_db()

    logging.info("Iniciando o serviço AI-Processor...")

    api_client = APIClient(base_url=API_BASE_URL)
    plate_detector = PlateDetector(model_path="yolov8n.pt")
    active_threads = {}
    db_session = database.SessionLocal()

    app = Flask(__name__)

    @app.route('/lpr-webhook', methods=['POST'])
    def webhook_listener():
        data = request.json
        logging.info("--- Webhook Recebido em /lpr-webhook ---")
        logging.info(data) # O log já mostra o JSON, mas o ficheiro é uma garantia extra

        webhook_processor_thread = Thread(target=process_lpr_webhook, args=(data, api_client, db_session))
        webhook_processor_thread.start()

        return jsonify({"status": "received"}), 200

    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False), daemon=True)
    flask_thread.start()
    logging.info("Servidor de Webhook iniciado e à escuta em http://0.0.0.0:5000/lpr-webhook")

    try:
        while True:
            if not onoff_suporte.verificar_status_gt_ia():
                if active_threads:
                    logging.info("GT IA (YOLO) foi desativada. Parando todos os processamentos RTSP...")
                    for cam_id in list(active_threads.keys()):
                        active_threads[cam_id]['info']['thread_active'] = False
                        active_threads[cam_id]['thread'].join()
                        del active_threads[cam_id]
                logging.info("GT IA (RTSP) está desativada. Aguardando para reativar...")
                time.sleep(30)
                continue
            
            logging.info("Buscando lista de câmaras para processamento RTSP...")
            # ... (resto do loop while igual ao que já tinha)
            time.sleep(60)

    except KeyboardInterrupt:
        logging.info("AI-Processor está a ser desligado...")
        for cam_id in active_threads:
            active_threads[cam_id]['info']['thread_active'] = False
            active_threads[cam_id]['thread'].join()
    finally:
        db_session.close()
        logging.info("Serviço encerrado.")

if __name__ == "__main__":
    main()