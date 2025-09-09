import os
import requests
import logging
from typing import List, Dict, Any

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("ADMIN_API_KEY")
        if not self.api_key:
            self.logger.error("A variável de ambiente ADMIN_API_KEY não está definida.")
            raise ValueError("Chave de API não encontrada.")
        self.headers = {"X-API-Key": self.api_key}

    def check_api_health(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                self.logger.info("API do backend está disponível!")
                return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Não foi possível conectar à API do backend: {e}")
        return False

    def get_cameras_from_api(self) -> List[Dict[str, Any]]:
        # ALTERAÇÃO IMPORTANTE: Apontar para a nova rota interna
        internal_cameras_url = f"{self.base_url}/api/v1/internal/cameras"
        self.logger.info(f"A buscar câmaras do endpoint interno: {internal_cameras_url}")
        
        try:
            response = requests.get(internal_cameras_url, headers=self.headers)
            if response.status_code == 200:
                self.logger.info(f"Encontradas {len(response.json())} câmaras para processar.")
                return response.json()
            elif response.status_code == 401:
                self.logger.error("ERRO 401: A chave de API interna (ADMIN_API_KEY) é inválida. Verifique o ficheiro .env em ambos os serviços.")
            else:
                self.logger.error(f"Erro ao buscar câmaras. Status: {response.status_code}, Resposta: {response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de conexão ao buscar câmaras: {e}")
        return []

    def send_sighting_to_api(self, plate: str, image_filename: str, camera_id: int):
        # A rota de avistamentos precisa ser protegida da mesma forma (assumindo que seja interna)
        # Se for para utilizadores, a lógica terá de ser diferente. Por agora, vamos usar a chave de API.
        sighting_url = f"{self.base_url}/api/v1/sightings/"
        files = {'image_file': (os.path.basename(image_filename), open(image_filename, 'rb'), 'image/jpeg')}
        data = {"plate": plate, "camera_id": camera_id}
        
        try:
            response = requests.post(sighting_url, files=files, data=data, headers=self.headers)
            if response.status_code == 201:
                self.logger.info(f"Avistamento da placa {plate} enviado com sucesso.")
            else:
                self.logger.error(f"Falha ao enviar avistamento. Status: {response.status_code}, Resposta: {response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de conexão ao enviar avistamento: {e}")
        finally:
            if 'image_file' in files:
                files['image_file'][1].close()
