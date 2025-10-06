# # event-listener/listener.py
# import os
# import time
# import requests
# import pika
# import json
# import threading
# import logging
# import base64
# from requests.auth import HTTPDigestAuth

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(message)s')

# # --- LEITURA DAS VARIÁVEIS DE AMBIENTE ---
# RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')

# # --- CORREÇÃO APLICADA AQUI ---
# # As variáveis de ambiente devem corresponder às que o docker-compose espera do ficheiro .env
# RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
# RABBITMQ_PASS = os.getenv('RABBITMQ_PASSWORD', 'guest')
# # --- FIM DA CORREÇÃO ---

# BACKEND_API_URL = os.getenv('BACKEND_URL', 'http://backend:8000')
# ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')
# LPR_EVENT_QUEUE = 'lpr_events'

# monitored_cameras = {}
# lock = threading.Lock()

# def parse_multipart_stream(response, camera, pika_channel):
#     content_boundary = None
#     content_type_header = response.headers.get('Content-Type', '')
#     if 'boundary=' in content_type_header:
#         content_boundary = content_type_header.split('boundary=')[1].encode('utf-8')
#     if not content_boundary:
#         logging.error(f"[{camera['name']}] Boundary não encontrado. Encerrando.")
#         return
#     buffer = b''
#     last_event_data = None
#     for chunk in response.iter_content(chunk_size=4096):
#         buffer += chunk
#         while content_boundary in buffer:
#             part, buffer = buffer.split(content_boundary, 1)
#             if not part.strip(): continue
#             try:
#                 headers_bytes, content_bytes = part.split(b'\r\n\r\n', 1)
#                 headers = headers_bytes.decode('utf-8', errors='ignore')
#                 if 'Content-Type: text/plain' in headers:
#                     event_text = content_bytes.decode('utf-8', errors='ignore').strip()
#                     if 'TrafficJunction' in event_text:
#                         plate_number = None
#                         for line in event_text.split('\r\n'):
#                             if 'TrafficCar.PlateNumber' in line:
#                                 plate_number = line.split('=')[1].strip()
#                                 break
#                         if plate_number:
#                             last_event_data = {'camera_id': camera['id'], 'plate_number': plate_number}
#                             logging.info(f"[{camera['name']}] Evento de placa detectado: {plate_number}")
#                 elif 'Content-Type: image/jpeg' in headers and last_event_data:
#                     logging.info(f"[{camera['name']}] Imagem recebida para o evento {last_event_data['plate_number']}")
#                     image_base64 = base64.b64encode(content_bytes).decode('utf-8')
#                     event_message = {
#                         "camera_id": last_event_data['camera_id'],
#                         "plate_number": last_event_data['plate_number'],
#                         "image_base64": image_base64,
#                         "source": "intelbras_push"
#                     }
#                     pika_channel.basic_publish(
#                         exchange='',
#                         routing_key=LPR_EVENT_QUEUE,
#                         body=json.dumps(event_message),
#                         properties=pika.BasicProperties(delivery_mode=2)
#                     )
#                     logging.info(f"[{camera['name']}] Evento de {last_event_data['plate_number']} publicado na fila '{LPR_EVENT_QUEUE}'")
#                     last_event_data = None
#             except Exception as e:
#                 logging.warning(f"[{camera['name']}] Erro ao processar parte do fluxo: {e}")
#                 last_event_data = None

# def listen_to_camera_events(camera, pika_channel):
#     camera_name = camera.get('name', f"ID-{camera['id']}")
#     logging.info(f"[{camera_name}] Iniciando escuta.")
#     try:
#         rtsp_url = camera['rtsp_url']
#         user = rtsp_url.split('://')[1].split(':')[0]
#         password = rtsp_url.split(':')[2].split('@')[0]
#         host = rtsp_url.split('@')[1].split('/')[0].split(':')[0]
#     except Exception:
#         logging.error(f"[{camera_name}] URL RTSP mal formatada: {camera['rtsp_url']}")
#         return
#     event_url = f"http://{host}/cgi-bin/snapManager.cgi?action=attachFileProc&Events=[TrafficJunction]"
#     auth = HTTPDigestAuth(user, password)
#     while True:
#         try:
#             logging.info(f"[{camera_name}] Conectando a {event_url}...")
#             with requests.get(event_url, auth=auth, stream=True, timeout=(5, 60)) as response:
#                 if response.status_code == 200:
#                     logging.info(f"[{camera_name}] Conexão estabelecida.")
#                     parse_multipart_stream(response, camera, pika_channel)
#                 elif response.status_code == 401:
#                     logging.error(f"[{camera_name}] Falha na autenticação.")
#                     break
#                 else:
#                     logging.warning(f"[{camera_name}] Erro ao conectar: {response.status_code}. Tentando em 30s.")
#         except requests.exceptions.RequestException as e:
#             logging.warning(f"[{camera_name}] Exceção na conexão: {e}. Tentando em 30s.")
#         time.sleep(30)

# def get_cameras_from_api():
#     try:
#         headers = {'X-API-Key': ADMIN_API_KEY}
#         response = requests.get(f"{BACKEND_API_URL}/api/v1/internal/cameras/by_type/intelbras_push", headers=headers)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.error(f"Erro ao buscar câmeras da API: {response.status_code} {response.text}")
#             return []
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Não foi possível conectar à API do backend: {e}")
#         return []

# def main():
#     logging.info("Iniciando serviço Event Listener...")
    
#     connection = None
#     while not connection:
#         try:
#             # As credenciais são lidas das variáveis de ambiente corretas
#             credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
#             parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
#             connection = pika.BlockingConnection(parameters)
#             logging.info("Conexão com RabbitMQ estabelecida com sucesso.")
#         except pika.exceptions.ProbableAuthenticationError as e:
#             logging.error(f"Falha na autenticação com RabbitMQ: {e}. Verifique as variáveis de ambiente RABBITMQ_USER e RABBITMQ_PASSWORD. Tentando novamente em 20 segundos...")
#             time.sleep(20)
#         except pika.exceptions.AMQPConnectionError as e:
#             logging.error(f"Não foi possível conectar ao RabbitMQ: {e}. Tentando novamente em 20 segundos...")
#             time.sleep(20)

#     channel = connection.channel()
#     channel.queue_declare(queue=LPR_EVENT_QUEUE, durable=True)
#     logging.info(f"Fila '{LPR_EVENT_QUEUE}' declarada.")
    
#     while True:
#         logging.info("Verificando lista de câmeras...")
#         cameras = get_cameras_from_api()
#         with lock:
#             current_ids = set(monitored_cameras.keys())
#             api_ids = {cam['id'] for cam in cameras}
#             new_camera_ids = api_ids - current_ids
            
#             for cam_id in new_camera_ids:
#                 camera = next((c for c in cameras if c['id'] == cam_id), None)
#                 if camera:
#                     logging.info(f"Nova câmera encontrada: {camera.get('name')}")
#                     thread = threading.Thread(target=listen_to_camera_events, args=(camera, channel), name=f"Camera-{camera.get('name', cam_id)}", daemon=True)
#                     thread.start()
#                     monitored_cameras[cam_id] = thread
#         time.sleep(60)

# if __name__ == '__main__':
#     # Pequeno atraso para garantir que o RabbitMQ está pronto
#     time.sleep(20)
#     main()