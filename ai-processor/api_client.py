import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        if not self.api_key:
            # Lança um erro crítico se a chave da API não estiver configurada
            logger.critical("A chave da API (api_key) não foi fornecida.")
            raise ValueError("A chave da API (api_key) não foi fornecida.")

    def _get_auth_headers(self):
        """Retorna os cabeçalhos de autenticação para as requisições."""
        return {"X-API-Key": self.api_key}

    def send_sighting(self, sighting_data: dict):
        """
        Envia uma nova detecção de placa para a API.
        O formato do timestamp deve ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).
        """
        if not all(k in sighting_data for k in ["license_plate", "camera_id", "confidence"]):
            logger.error(f"Dados de detecção incompletos: {sighting_data}")
            return None

        try:
            payload = {
                "license_plate": sighting_data["license_plate"],
                "timestamp": datetime.utcnow().isoformat() + "Z", # Adicionado 'Z' para UTC
                "camera_id": sighting_data["camera_id"],
                "confidence": sighting_data["confidence"]
            }
            headers = self._get_auth_headers()
            # CORREÇÃO: URL ajustado para /sightings (sem a barra final)
            url = f"{self.base_url}/sightings"
            
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            response.raise_for_status() # Lança exceção para respostas com status de erro (4xx ou 5xx)
            
            logger.info(f"Detecção enviada com sucesso para a API: {payload.get('license_plate')}")
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP ao enviar detecção para a API: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erro de conexão ao enviar detecção para a API: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout ao enviar detecção para a API: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro inesperado ao enviar detecção para a API: {e}")
            
        return None

    # Adicione os métodos que faltam e que são chamados em main.py
    def is_api_available(self):
        """Verifica se a API está disponível."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_cameras(self):
        """Busca as câmeras da API."""
        try:
            headers = self._get_auth_headers()
            # CORREÇÃO: URL ajustado para /cameras (sem a barra final)
            response = requests.get(f"{self.base_url}/cameras", headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP ao buscar câmeras: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar câmeras: {e}")
        return None