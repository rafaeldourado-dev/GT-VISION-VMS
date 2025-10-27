import logging
import time
import os # Adicionado para ler variáveis de ambiente
import json
import pika
from threading import Thread, Event
import requests # Adicionado para chamadas HTTP
import cv2
from typing import Dict
import redis

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from api_client import APIClient
from detection import PlateDetector

API_BASE_URL = os.getenv("API_BASE_URL", "http://gt-vision-backend:8000")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "gt-vision-rabbitmq")
REDIS_HOST = os.getenv("REDIS_HOST", "gt-vision-redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
API_KEY = os.getenv("ADMIN_API_KEY") # CORRIGIDO: Usa a variável de ambiente correta
QUEUE_NAME = 'camera_processing_queue'
DUPLICATE_CHECK_TTL_SECONDS = int(os.getenv("DUPLICATE_CHECK_TTL_SECONDS", "30"))


# Dicionário para manter o controle dos threads de processamento e seus eventos de parada
processing_threads: Dict[int, Dict[str, any]] = {}

def process_camera_stream(camera_info: dict, detector: PlateDetector, api_client: APIClient, stop_event: Event):
    rtsp_url = camera_info.get("rtsp_url")
    camera_id = camera_info.get("id")
    camera_name = camera_info.get("name", f"Câmera {camera_id}")

    # --- CORREÇÃO APLICADA AQUI ---
    # Força o OpenCV a usar TCP para o transporte RTSP. Isso é mais robusto do que depender da variável de ambiente do docker-compose.
    # Adiciona um buffer maior para lidar com picos e um timeout para evitar bloqueios.
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|buffer_size;1000000"

    # --- CORREÇÃO APLICADA AQUI ---
    # Adiciona o timeout de forma inteligente, usando '&' se a URL já tiver '?'
    timeout_param = "timeout=5000000" # 5 segundos em microssegundos
    separator = '&' if '?' in rtsp_url else '?'
    rtsp_url_with_timeout = f"{rtsp_url}{separator}{timeout_param}"
    # ---------------------------------
    logging.info(f"AI-Processor para câmera {camera_name} (ID: {camera_id}) tentando conectar a: {rtsp_url_with_timeout}")
    logging.info(f"Iniciando processamento para a câmera: {camera_name} ({rtsp_url}) usando transporte TCP.")
    
    cap = None
    retry_count = 0
    # --- ALTERAÇÃO CRÍTICA: 'max_retries' removido ---
    # max_retries = 5 (REMOVIDO)
    retry_delay = 5 # segundos

    # NOVO: Variáveis para tolerância de falhas de leitura de frames
    consecutive_read_failures = 0
    MAX_CONSECUTIVE_READ_FAILURES = 30 # Aumentado para 30 frames (~1 segundo)

    while not stop_event.is_set():
        if cap is None or not cap.isOpened():
            # NOVO: Reseta o contador de falhas de leitura ao tentar uma nova conexão
            consecutive_read_failures = 0 # Corrigido: Usar a variável correta
            
            # --- ALTERAÇÃO CRÍTICA: Bloco 'if retry_count >= max_retries' removido ---
            # O processador não vai mais desistir.
            
            # Log atualizado para não mostrar mais o max_retries
            logging.warning(f"Stream da câmera {camera_name} indisponível. Tentando (re)conectar em {retry_delay} segundos... (Tentativa {retry_count + 1})")
            time.sleep(retry_delay)
            cap = cv2.VideoCapture(rtsp_url_with_timeout, cv2.CAP_FFMPEG) # Usa a URL com timeout
            retry_count += 1
            retry_delay = min(retry_delay * 2, 60) # Aumenta o delay, no máximo 60s
            continue

        ret, frame = cap.read()
        
        # --- LÓGICA DE TOLERÂNCIA A FALHAS APRIMORADA ---
        if not ret:
            consecutive_read_failures += 1
            
            if consecutive_read_failures >= MAX_CONSECUTIVE_READ_FAILURES:
                logging.warning(f"{consecutive_read_failures} frames consecutivos não recebidos da câmera {camera_name}. A conexão foi considerada perdida. Iniciando ciclo de reconexão.")
                cap.release()
                cap = None
                retry_count = 0 # Reseta as tentativas para iniciar o ciclo de reconexão
                time.sleep(1) # Pausa para evitar loop de erro imediato
            else:
                # Tolera a falha momentânea e tenta ler novamente no próximo ciclo
                logging.debug(f"Frame não recebido (falha {consecutive_read_failures}/{MAX_CONSECUTIVE_READ_FAILURES}). Tolerando falha momentânea.")
                # Pausa mínima para não sobrecarregar o loop e tentar de novo rapidamente
                time.sleep(1/60) # Espera o tempo de um frame a 60fps
            continue
        
        # SUCESSO: Reseta o contador de falhas e continua o processamento
        consecutive_read_failures = 0
        
        try:
            detections = detector.detect_and_recognize(frame, camera_id)
            
            for detection in detections:
                plate_text = detection.get("plate")
                image_path = detection.get("image_path")
                accuracy = detection.get("accuracy", 0.0) # Assume 0.0 se não houver acurácia

                if plate_text and image_path and accuracy >= 0.70: # Filtra por acurácia
                    # Verifica duplicidade no Redis
                    # A chave é única para placa + câmera, com um TTL
                    duplicate_key = f"sighting:{camera_id}:{plate_text}"
                    if redis_client and redis_client.setnx(duplicate_key, "1"): # setnx retorna 1 se a chave foi definida (não existia)
                        redis_client.expire(duplicate_key, DUPLICATE_CHECK_TTL_SECONDS)
                        logging.info(f"Placa detectada pela câmera {camera_name}: {plate_text} (Acurácia: {accuracy:.2f})")
                        api_client.send_sighting_to_api(
                            plate=plate_text,
                            image_filename=image_path,
                            camera_id=camera_id,
                            accuracy=accuracy # NOVO: Passa a acurácia para o backend
                        )
                    else:
                        logging.debug(f"Placa {plate_text} da câmera {camera_name} ignorada (duplicada ou acurácia baixa).")

        except Exception as e:
            logging.error(f"Erro durante o processamento do frame da câmera {camera_name}: {e}")

    if cap and cap.isOpened():
        cap.release()
    logging.info(f"Processamento para a câmera {camera_name} encerrado.")

def start_processing(camera_info: dict, detector: PlateDetector, api_client: APIClient):
    camera_id = camera_info.get("id")
    if camera_id in processing_threads:
        logging.warning(f"O processamento para a câmera ID {camera_id} já está em execução.")
        return

    stop_event = Event()
    thread = Thread(target=process_camera_stream, args=(camera_info, detector, api_client, stop_event))
    thread.start()
    processing_threads[camera_id] = {"thread": thread, "stop_event": stop_event}
    logging.info(f"Thread de processamento iniciada para a câmera ID {camera_id}.")

def stop_processing(camera_id: int):
    if camera_id not in processing_threads:
        logging.warning(f"Nenhum processamento em execução para a câmera ID {camera_id} para parar.")
        return

    logging.info(f"Solicitando parada do processamento para a câmera ID {camera_id}...")
    processing_threads[camera_id]["stop_event"].set()
    processing_threads[camera_id]["thread"].join(timeout=15) # Espera o thread terminar
    del processing_threads[camera_id]
    logging.info(f"Processamento para a câmera ID {camera_id} finalizado e removido.")

def message_callback(ch, method, properties, body):
    """Função chamada quando uma mensagem é recebida do RabbitMQ."""
    try:
        message = json.loads(body)
        action = message.get("action")
        camera_info = message.get("camera_info")
        camera_id = camera_info.get("id")

        logging.info(f"Comando '{action}' recebido para a câmera ID {camera_id}")

        if action == "start":
            # Reutiliza os objetos detector e api_client globais
            start_processing(camera_info, plate_detector, api_client)
        elif action == "stop":
            stop_processing(camera_id)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        logging.error("Erro ao decodificar a mensagem JSON do RabbitMQ.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logging.error(f"Erro inesperado ao processar mensagem: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def initialize_active_cameras(detector: PlateDetector, api_client: APIClient):
    """Busca e inicia o processamento para todas as câmeras ativas no backend."""
    logging.info("Buscando câmeras ativas para iniciar o processamento automático...")
    try:
        # Utiliza o método do api_client que já usa a rota interna e a API Key
        cameras = api_client.get_cameras_from_api()
        
        active_cameras = [cam for cam in cameras if cam.get("is_active")]

        if not active_cameras:
            logging.info("Nenhuma câmera ativa encontrada para processamento inicial.")
            return

        logging.info(f"Encontradas {len(active_cameras)} câmeras ativas. Iniciando threads...")
        for camera in active_cameras:
            # --- NOVO: Garante que o stream está ativo no MediaMTX ---
            # -----------------------------------------------------------

            start_processing(camera, detector, api_client)
            
    except Exception as e:
        logging.error(f"Não foi possível buscar as câmeras do backend: {e}. O processamento automático inicial não será executado.")

def main():
    logging.info("Iniciando o serviço AI-Processor...")
    
    # Estas instâncias serão compartilhadas por todos os threads
    global api_client, plate_detector, redis_client
    
    if not API_KEY:
        logging.error("A variável de ambiente ADMIN_API_KEY não está definida. O serviço não pode autenticar com o backend.")
        return
    api_client = APIClient(base_url=API_BASE_URL, api_key=API_KEY)
    plate_detector = PlateDetector(model_path="yolov8n.pt")

    # NOVO: Inicializa o cliente Redis
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        redis_client.ping()
        logging.info("Conexão com Redis estabelecida.")
    except redis.exceptions.ConnectionError as e:
        logging.error(f"Não foi possível conectar ao Redis: {e}. A funcionalidade de detecção de duplicatas não estará disponível.")
    
    # Inicia o processamento para câmeras já ativas
    # Esta função agora só será chamada depois que o /api/ready do backend estiver OK.
    initialize_active_cameras(plate_detector, api_client)

    # Conecta-se ao RabbitMQ
    connection = None
    while not connection:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            logging.info("Conexão com RabbitMQ estabelecida.")
        except pika.exceptions.AMQPConnectionError:
            logging.warning("Aguardando o RabbitMQ... tentando novamente em 5 segundos.")
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Configura o consumo da fila
    channel.basic_qos(prefetch_count=1) # Processa uma mensagem de cada vez
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=message_callback)

    try:
        logging.info("Aguardando por comandos de processamento de câmera. Pressione CTRL+C para sair.")
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info("Encerrando o AI-Processor...")
        channel.stop_consuming()
    finally:
        connection.close()
        logging.info("Conexão com RabbitMQ fechada.")
        
if __name__ == "__main__":
    main()