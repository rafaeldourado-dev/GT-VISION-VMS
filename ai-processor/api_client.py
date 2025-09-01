import os
import requests
import logging
import time

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://backend:8000")
        self.api_key = os.getenv("ADMIN_API_KEY")
        if not self.api_key:
            raise ValueError("ADMIN_API_KEY não foi definida nas variáveis de ambiente.")

    def _get_auth_headers(self):
        return {"X-API-Key": self.api_key}

    def get_active_cameras(self):
        """Busca todas as câmaras com IA habilitada na API."""
        try:
            headers = self._get_auth_headers()
            url = f"{self.base_url}/cameras/service/active"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            cameras = response.json()
            logger.info(f"Encontradas {len(cameras)} câmaras ativas para processamento.")
            return cameras
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar câmaras ativas da API: {e}")
            return []

    def send_sighting(self, sighting_data: dict):
        """Envia uma nova leitura de matrícula para a API."""
        try:
            headers = self._get_auth_headers()
            url = f"{self.base_url}/sightings/"
            response = requests.post(url, json=sighting_data, headers=headers, timeout=5)
            response.raise_for_status()
            logger.info(f"Leitura enviada com sucesso para a API: {sighting_data.get('license_plate')}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar leitura para a API: {e}")
            return None