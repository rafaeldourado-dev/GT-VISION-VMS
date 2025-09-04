# backend/app/messaging.py
import pika
import json
import logging
from .config import settings
from . import schemas

logger = logging.getLogger(__name__)

QUEUE_NAME = 'camera_processing_queue'

def get_rabbitmq_connection():
    """Cria e retorna uma conexão com o RabbitMQ."""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        logger.info("Conexão com RabbitMQ estabelecida com sucesso.")
        return connection
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Falha ao conectar com o RabbitMQ: {e}")
        return None

def publish_camera_command(action: str, camera: schemas.Camera):
    """
    Publica um comando para iniciar ou parar o processamento de uma câmera.

    Args:
        action (str): A ação a ser executada ('start' ou 'stop').
        camera (schemas.Camera): O objeto da câmera com seus dados.
    """
    connection = get_rabbitmq_connection()
    if not connection:
        return

    try:
        channel = connection.channel()
        
        # Garante que a fila exista e seja durável (sobrevive a reinicializações do RabbitMQ)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        
        # A mensagem precisa ser serializável, então usamos o schema da câmera
        message_body = {
            "action": action,
            "camera_info": {
                "id": camera.id,
                "name": camera.name,
                "rtsp_url": camera.rtsp_url,
                "client_id": camera.client_id
            }
        }
        
        message_str = json.dumps(message_body)
        
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message_str,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Torna a mensagem persistente
            ))
            
        logger.info(f"Comando '{action}' para a câmera ID {camera.id} publicado na fila '{QUEUE_NAME}'.")

    except Exception as e:
        logger.error(f"Erro ao publicar mensagem no RabbitMQ: {e}")
    finally:
        if connection.is_open:
            connection.close()