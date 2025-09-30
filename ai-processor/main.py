import logging
import time
import os
import uuid
from threading import Thread
import cv2

# --- NOVAS IMPORTAÇÕES PARA AS NOVAS FUNCIONALIDADES ---
# Módulos que você criou nos passos anteriores
from alert_system import logs, alarmes, onoff_suporte
from database import database, crud
from sqlalchemy.orm import Session

# Módulos que você já tinha
from api_client import APIClient
from detection import PlateDetector

# --- CONFIGURAÇÃO ---
API_BASE_URL = "http://gt-vision-backend:8000"
PENDING_TRAINING_DIR = "pending_training"
os.makedirs(PENDING_TRAINING_DIR, exist_ok=True)


def salvar_para_treinamento(frame_completo, texto_da_placa):
    """
    Salva o frame completo do vídeo e a placa lida para o próximo ciclo de treinamento.
    (Esta função permanece exatamente como a sua original)
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
    Função principal de processamento de vídeo, agora com a sessão do banco de dados.
    """
    rtsp_url = camera_info.get("rtsp_url")
    camera_id = camera_info.get("id")
    camera_name = camera_info.get("name", f"Câmera {camera_id}")
    
    logging.info(f"Iniciando processamento para a câmera: {camera_name} ({rtsp_url})")
    
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        logging.error(f"Não foi possível abrir o stream de vídeo para a câmera {camera_name}.")
        return

    # Loop principal modificado para ser controlado pelo main loop
    while camera_info.get('thread_active', True): # A thread irá verificar esta flag
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
                    logging.info(f"Placa detectada pela câmera {camera_name}: {plate_text}")
                    
                    # 1. Envia o resultado para a API principal (como antes)
                    api_client.send_sighting_to_api(
                        plate=plate_text,
                        image_filename=image_path,
                        camera_id=camera_id
                    )
                    
                    # 2. Salva o frame completo para treinamento futuro (como antes)
                    salvar_para_treinamento(frame, plate_text)

                    # 3. <<< NOVA FUNCIONALIDADE AQUI >>>
                    # Salva/Atualiza a informação no banco de dados local do AI-Processor
                    crud.get_or_create_vehicle(db=db_session, plate=plate_text)
                    logging.info(f"Placa '{plate_text}' registrada no banco de dados local.")

        except Exception as e:
            logging.error(f"Erro durante o processamento do frame da câmera {camera_name}: {e}")
        
        # Pequena pausa para não sobrecarregar a CPU
        time.sleep(0.01)

    cap.release()
    logging.info(f"Processamento para a câmera {camera_name} encerrado.")


def main():
    """
    Função principal refatorada para rodar continuamente e gerir as threads dinamicamente.
    """
    # 1. Inicia os novos sistemas de log e banco de dados
    logs.configurar_logging()
    database.init_db()
    
    logging.info("Iniciando o serviço AI-Processor...")
    
    # Exemplo de como usar o controle ON/OFF (você pode criar um script separado para isso)
    # onoff_suporte.ativar_gt_ia() # para ligar
    # onoff_suporte.desativar_gt_ia() # para desligar
    
    api_client = APIClient(base_url=API_BASE_URL)
    plate_detector = PlateDetector(model_path="yolov8n.pt")
    
    # Dicionário para manter o controlo das threads ativas e suas informações
    active_threads = {}
    
    # Cria uma única sessão de banco de dados para ser usada pelo serviço
    db_session = database.SessionLocal()

    try:
        while True:
            # 2. Verifica o status do controlo ON/OFF a cada ciclo
            if not onoff_suporte.verificar_status_gt_ia():
                if active_threads:
                    logging.info("GT IA (YOLO) foi desativada. Parando todos os processamentos...")
                    for cam_id in list(active_threads.keys()):
                        active_threads[cam_id]['info']['thread_active'] = False
                        active_threads[cam_id]['thread'].join()
                        del active_threads[cam_id]
                logging.info("GT IA está desativada. Aguardando para reativar...")
                time.sleep(30)
                continue

            # 3. Busca a lista de câmaras atualizada do backend
            logging.info("Buscando lista de câmaras atualizada do backend...")
            cameras = api_client.get_cameras_from_api() # Use a sua função que busca da API
            
            if cameras is None:
                logging.error("Não foi possível buscar a lista de câmaras. Tentando novamente em 60s.")
                time.sleep(60)
                continue
            
            current_camera_ids = {cam['id'] for cam in cameras if cam.get("is_active")}
            active_thread_ids = set(active_threads.keys())
            
            # Iniciar threads para novas câmaras
            for cam_info in cameras:
                cam_id = cam_info['id']
                if cam_info.get("is_active") and cam_id not in active_thread_ids:
                    logging.info(f"Nova câmera ativa detectada: {cam_info['name']}. Iniciando processamento.")
                    cam_info['thread_active'] = True
                    thread = Thread(target=process_camera_stream, args=(cam_info, plate_detector, api_client, db_session), daemon=True)
                    thread.start()
                    active_threads[cam_id] = {'thread': thread, 'info': cam_info}
            
            # Parar threads para câmaras que foram removidas ou desativadas
            for cam_id in active_thread_ids - current_camera_ids:
                logging.info(f"Câmera ID {cam_id} não está mais ativa. Parando processamento.")
                active_threads[cam_id]['info']['thread_active'] = False
                active_threads[cam_id]['thread'].join(timeout=15) # Espera a thread terminar
                del active_threads[cam_id]
            
            # 4. Exemplo de verificação de logs e alarmes
            falhas_detectadas = logs.verificar_logs_por_violacoes("ERRO")
            alarmes.processar_falhas(falhas_detectadas)
            
            # Intervalo de 60 segundos antes de verificar a lista de câmaras novamente
            logging.info(f"Verificação concluída. {len(active_threads)} câmera(s) em processamento. Próxima verificação em 60s.")
            time.sleep(60)

    except KeyboardInterrupt:
        logging.info("AI-Processor está a ser desligado. Aguardando threads terminarem...")
        for cam_id in active_threads:
            active_threads[cam_id]['info']['thread_active'] = False
            active_threads[cam_id]['thread'].join()
    finally:
        db_session.close()
        logging.info("Sessão do banco de dados fechada. Serviço encerrado.")

if __name__ == "__main__":
    main()