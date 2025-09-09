import requests
import logging
import os

class APIClient:
    """
    Cliente para comunicar com a API do backend GT-Vision.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        # Estratégia de autenticação: Carregar um token de um ficheiro ou variável de ambiente
        # Isto é mais seguro do que deixar o token no código.
        self.auth_token = os.getenv("API_ACCESS_TOKEN", None)
        self.headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}


    def check_api_health(self) -> bool:
        """Verifica se a API do backend está acessível."""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            response.raise_for_status()
            self.logger.info("API está disponível!")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API indisponível: {e}")
            return False

    def get_cameras_from_api(self) -> list:
        """Busca a lista de câmeras ativas da API do backend."""
        try:
            api_url = f"{self.base_url}/api/v1/cameras/"
            response = requests.get(api_url, headers=self.headers, timeout=10)

            if response.status_code == 401:
                self.logger.error("Erro de autenticação (401). O ai-processor precisa de um token de acesso válido.")
                return []

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Erro HTTP ao buscar câmeras: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de conexão ao buscar câmeras: {e}")
        return []

    def send_sighting_to_api(self, plate: str, image_filename: str, camera_id: int):
        """Envia um novo avistamento de veículo para a API."""
        try:
            api_url = f"{self.base_url}/api/v1/sightings/vehicle"
            payload = {
                "license_plate": plate,
                "image_filename": image_filename,
                "camera_id": camera_id
            }
            response = requests.post(api_url, json=payload, timeout=10) # Não precisa de token para este endpoint
            response.raise_for_status()
            self.logger.info(f"Avistamento da placa '{plate}' enviado com sucesso para a API.")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Falha ao enviar avistamento para a API: {e}")