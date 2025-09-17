import os
import requests
import logging
from fastapi import FastAPI, Request, HTTPException, status
from .parsers import get_parser

# --- Configurações Corrigidas ---
# A URL correta, usando o nome do serviço 'backend' do docker-compose.yml
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_KEY = os.getenv("ADMIN_API_KEY")

app = FastAPI(title="LPR Event Handler")
logging.basicConfig(level=logging.INFO)

@app.post("/event/{brand}/{camera_id}", status_code=status.HTTP_201_CREATED)
async def handle_lpr_event(brand: str, camera_id: int, request: Request):
    parser = get_parser(brand)
    if not parser:
        raise HTTPException(status_code=400, detail=f"Marca '{brand}' não suportada.")

    request_data = await request.body()
    parsed_data = parser.parse(request_data)

    if not parsed_data or "license_plate" not in parsed_data:
        raise HTTPException(status_code=422, detail="Falha ao extrair placa do evento.")

    # --- Envia os dados para o Backend (imitando o ai-processor) ---
    sighting_payload = {
        "license_plate": parsed_data["license_plate"],
        "camera_id": camera_id,
    }

    # O endpoint interno do seu backend para receber avistamentos
    sighting_url = f"{BACKEND_URL}/api/v1/internal/sightings"
    headers = {"X-API-Key": API_KEY}
    
    try:
        logging.info(f"Enviando avistamento para: {sighting_url}")
        response = requests.post(sighting_url, json=sighting_payload, headers=headers)
        response.raise_for_status()
        logging.info(f"Avistamento de '{brand}' (cam {camera_id}) enviado para o backend com sucesso.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao enviar avistamento para o backend: {e}")
        raise HTTPException(status_code=502, detail="Erro de comunicação com o serviço de backend.")
