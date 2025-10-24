import os
import requests
import logging
from typing import List, Dict, Any

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        if not self.api_key:
            self.logger.error("A chave de API não foi fornecida ao APIClient.")
            raise ValueError("Chave de API não fornecida.")
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
        internal_cameras_url = f"{self.base_url}/api/v1/internal/cameras"
        self.logger.info(f"A buscar câmaras do endpoint interno: {internal_cameras_url}")
        
        try:
            response = requests.get(internal_cameras_url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                self.logger.error("Erro de autenticação (403 Forbidden). Verifique se a ADMIN_API_KEY está correta e corresponde entre o .env do backend e o docker-compose do ai-processor.")
            else:
                self.logger.error(f"Erro ao buscar câmaras. Status: {response.status_code}, Resposta: {response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de conexão ao buscar câmaras: {e}")
        return []

    def start_stream_proxy(self, camera_id: int):
        """
        Solicita ao backend que inicie o proxy de stream para uma câmera no MediaMTX.
        Isso garante que o stream esteja disponível na URL interna.
        """
        proxy_url = f"{self.base_url}/api/v1/streaming/start/{camera_id}"
        try:
            # Usamos POST, como definido na rota do backend. A resposta não é crítica aqui.
            response = requests.post(proxy_url, headers=self.headers)
            if response.status_code == 200:
                self.logger.info(f"Proxy para câmera {camera_id} ativado/verificado com sucesso.")
            else:
                self.logger.warning(f"Falha ao solicitar proxy para câmera {camera_id}. Status: {response.status_code}, Resposta: {response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de conexão ao solicitar proxy para câmera {camera_id}: {e}")

    def send_sighting_to_api(self, plate: str, image_filename: str, camera_id: int, accuracy: float):
        # --- CORREÇÃO APLICADA AQUI ---
        # O URL foi alterado para apontar para o endpoint interno correto.
        sighting_url = f"{self.base_url}/api/v1/internal/sightings"
        
        # O backend não espera um ficheiro, apenas os dados em JSON.
        # Se precisar de enviar a imagem, o backend teria de ser ajustado para recebê-la.
        # Por agora, vamos enviar apenas os dados que o backend espera.
        data = {
            "license_plate": plate,
            "camera_id": camera_id,
            "image_path": os.path.basename(image_filename), # Enviamos o caminho da imagem como texto
            "accuracy": accuracy # NOVO: Inclui a acurácia
        }
        
        try:
            # Enviamos os dados como JSON
            response = requests.post(sighting_url, json=data, headers=self.headers)
            if response.status_code == 201:
                self.logger.info(f"Avistamento da placa {plate} enviado com sucesso.")
            else:
                self.logger.error(f"Falha ao enviar avistamento. Status: {response.status_code}, Resposta: {response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de conexão ao enviar avistamento: {e}")