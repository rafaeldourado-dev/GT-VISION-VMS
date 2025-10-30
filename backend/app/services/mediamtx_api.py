import aiohttp
from typing import Dict, Any

from app.config import settings

class MediaMTXAPI:
    def __init__(self, base_url: str, user: str, password: str):
        self.base_url = base_url
        self.auth = None
        if user and password:
            self.auth = aiohttp.BasicAuth(user, password)
        # A sessão será criada por endpoint para garantir que está no loop de eventos correto

    async def _request(self, method: str, endpoint: str, json_data: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession(auth=self.auth) as session:
            try:
                async with session.request(method, url, json=json_data, timeout=5) as response:
                    response.raise_for_status()
                    if response.status == 200 and response.content_length and response.content_length > 0:
                        return await response.json()
                    return {}
            except aiohttp.ClientError as e:
                raise Exception(f"Failed to communicate with MediaMTX API at {url}: {e}") from e

    async def get_paths(self) -> Dict[str, Any]:
        """Lists all paths."""
        return await self._request("GET", "/v2/paths/list")

    async def get_path(self, path_name: str) -> Dict[str, Any]:
        """Gets a path configuration."""
        return await self._request("GET", f"/v2/paths/get/{path_name}")

    async def add_path(self, path_name: str, config: Dict[str, Any]):
        """Adds a new path."""
        # The API for adding/replacing is the same
        return await self.edit_path(path_name, config)

    async def edit_path(self, path_name: str, config: Dict[str, Any]):
        """Edits an existing path."""
        return await self._request("POST", f"/v2/paths/add/{path_name}", json_data=config)

    async def remove_path(self, path_name: str):
        """Removes a path."""
        return await self._request("POST", f"/v2/paths/delete/{path_name}")

# --- Instância Global ---
# Cria uma única instância do cliente da API para ser usada em toda a aplicação.
# As credenciais e a URL são obtidas a partir das configurações do ambiente.

mediamtx_api = MediaMTXAPI(
    base_url="http://media-server:9997", # Usa o nome do serviço do Docker Compose
    user=settings.MEDIA_SERVER_API_USER,
    password=settings.MEDIA_SERVER_API_PASS
)