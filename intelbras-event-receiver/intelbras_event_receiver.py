import os
import requests
from requests.auth import HTTPDigestAuth
import email
from io import BytesIO

# --- Configurações ---
CAMERA_IP = os.getenv("INTELBRAS_CAMERA_IP")
CAMERA_USER = os.getenv("INTELBRAS_CAMERA_USER")
CAMERA_PASSWORD = os.getenv("INTELBRAS_CAMERA_PASSWORD")
YOUR_SERVER_ENDPOINT = os.getenv("YOUR_SERVER_ENDPOINT")

# --- Eventos para se inscrever (Modifique conforme necessário) ---
# Exemplos: "VideoMotion", "FaceRecognition", "TrafficJunction"
# Use "All" para todos os eventos.
EVENTS_TO_SUBSCRIBE = os.getenv("INTELBRAS_EVENTS_TO_SUBSCRIBE", "All")

def parse_multipart_from_bytes(content, boundary):
    """
    Analisa um corpo de resposta multipart a partir de bytes.
    """
    # Adiciona a fronteira inicial para um split consistente
    body = b'--' + boundary.encode() + content
    parts = body.split(b'--' + boundary.encode())

    for part_bytes in parts:
        if part_bytes.strip():
            # A biblioteca email pode analisar mensagens no estilo MIME
            # Precisamos adicionar os headers, pois part_bytes é apenas o corpo da parte
            part_message = email.message_from_bytes(
                b'Content-Type: multipart/mixed; boundary=' + boundary.encode() + b'\r\n' +
                part_bytes
            )

            # Checa o tipo de conteúdo da parte
            payload = part_message.get_payload(0)
            part_content_type = payload.get_content_type()
            
            if part_content_type == 'text/plain':
                event_data_str = payload.get_payload(decode=True).decode('utf-8', errors='ignore')
                event_data_lines = event_data_str.strip().split('\r\n')
                event_json = {}
                for line in event_data_lines:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        event_json[key.strip()] = value.strip()
                
                # Se houver dados de evento, envie para o seu servidor
                if event_json:
                    print(f"Evento recebido: {event_json}")
                    send_to_your_server(event_json)

            elif part_content_type == 'image/jpeg':
                # Você pode opcionalmente lidar com a imagem aqui
                print("Imagem recebida (não está sendo processada).")


def send_to_your_server(data):
    """
    Envia os dados do evento para o seu endpoint de servidor.
    """
    if not YOUR_SERVER_ENDPOINT:
        print("A variável de ambiente YOUR_SERVER_ENDPOINT não está configurada. O evento não será enviado.")
        return

    try:
        response = requests.post(YOUR_SERVER_ENDPOINT, json=data, timeout=10)
        response.raise_for_status()
        print(f"Evento enviado com sucesso para {YOUR_SERVER_ENDPOINT}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar evento para o seu servidor: {e}")

def main():
    """
    Função principal para se inscrever nos eventos da câmera.
    """
    if not all([CAMERA_IP, CAMERA_USER, CAMERA_PASSWORD]):
        print("As variáveis de ambiente da câmera (IP, USER, PASSWORD) não estão configuradas. Saindo.")
        return

    # URL para se inscrever nos eventos, conforme a documentação da Intelbras
    subscription_url = f"http://{CAMERA_IP}/cgi-bin/snapManager.cgi"
    params = {
        'action': 'attachFileProc',
        'channel': 1,
        'heartbeat': 5,
        'Flags[0]': 'Event',
        'Events': f"[{EVENTS_TO_SUBSCRIBE}]"
    }

    print(f"Conectando à câmera em {CAMERA_IP} para os eventos: {EVENTS_TO_SUBSCRIBE}...")

    try:
        with requests.get(
            subscription_url,
            auth=HTTPDigestAuth(CAMERA_USER, CAMERA_PASSWORD),
            params=params,
            stream=True,
            timeout=20
        ) as response:
            response.raise_for_status()
            print("Conexão estabelecida. Aguardando eventos...")
            
            content_type = response.headers.get('content-type')
            if not content_type or 'boundary=' not in content_type:
                print("Erro: A resposta não é multipart ou não contém uma fronteira.")
                return

            boundary = content_type.split('boundary=')[1]
            
            buffer = b''
            for chunk in response.iter_content(chunk_size=1024):
                buffer += chunk
                # Verifica se temos uma fronteira completa no buffer para processar
                if boundary.encode() in buffer:
                    parts = buffer.split(b'--' + boundary.encode())
                    # Processa todas as partes completas, exceto a última que pode estar incompleta
                    for part in parts[:-1]:
                        if part:
                             parse_multipart_from_bytes(part, boundary)
                    # Mantém a última parte (potencialmente incompleta) no buffer
                    buffer = parts[-1]


    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com a câmera: {e}")
    except KeyboardInterrupt:
        print("Serviço interrompido pelo usuário.")

if __name__ == "__main__":
    main()
