from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import cv2
import numpy as np
import os
import uuid
import logging

from .. import crud, schemas
from ..dependencies import get_db

# Configuração do Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

router = APIRouter(
    prefix="/coletor",
    tags=["Coletor de Eventos"],
)

# --- CONFIGURAÇÃO DOS DIRETÓRIOS ---
# Usando caminhos absolutos dentro do container para consistência
PENDING_TRAINING_DIR = "/app/pending_training"
CAPTURES_DIR = "/app/captures"
os.makedirs(PENDING_TRAINING_DIR, exist_ok=True)
os.makedirs(CAPTURES_DIR, exist_ok=True)


def salvar_para_treinamento(frame_completo, texto_da_placa):
    """
    Salva o frame completo e a placa lida para o próximo ciclo de treinamento.
    """
    try:
        if not texto_da_placa or not texto_da_placa.strip():
            return
        unique_id = str(uuid.uuid4())
        nome_arquivo_imagem = f"{unique_id}.jpg"
        caminho_imagem = os.path.join(PENDING_TRAINING_DIR, nome_arquivo_imagem)
        cv2.imwrite(caminho_imagem, frame_completo)
        caminho_info = os.path.join(PENDING_TRAINING_DIR, f"{unique_id}.txt")
        with open(caminho_info, "w") as f:
            f.write(f"{nome_arquivo_imagem},{texto_da_placa}")
        logging.info(f"Coletor salvou para treino: Placa {texto_da_placa}")
    except Exception as e:
        logging.error(f"Coletor: Erro ao salvar dados para treinamento: {e}")


@router.post("/lpr", status_code=status.HTTP_201_CREATED)
async def handle_lpr_event(
    request: Request, # Adicionado para inspecionar todos os dados do formulário
    plate_text: str = Form(...),
    camera_id: int = Form(...),
    image: UploadFile = File(...),
    plate_bbox: str = Form(None, description="Coordenadas da placa no formato 'x,y,w,h'"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para receber eventos de LPR diretamente das câmeras.
    Se as coordenadas da placa (plate_bbox) forem enviadas, ele recorta a imagem da placa e salva.
    """
    # --- LOG DE DEPURACAO ---
    # Este log é crucial para você ver exatamente o que a câmera está enviando.
    form_data = await request.form()
    logging.info(f"Coletor recebeu dados da câmera: {form_data}")
    # -------------------------

    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=400, detail="Imagem inválida ou corrompida.")

    # Tarefa 1: Salva os dados para o futuro treinamento da nossa IA (imagem completa)
    salvar_para_treinamento(frame, plate_text)

    # Tarefa 2: Recorta e salva a imagem da placa se as coordenadas forem fornecidas
    plate_image_filename = None
    if plate_bbox:
        try:
            x, y, w, h = map(int, plate_bbox.split(','))
            if w > 0 and h > 0:
                plate_crop = frame[y:y+h, x:x+w]
                plate_image_filename = f"capture_{camera_id}_{plate_text}_{uuid.uuid4().hex[:8]}.jpg"
                save_path = os.path.join(CAPTURES_DIR, plate_image_filename)
                cv2.imwrite(save_path, plate_crop)
                logging.info(f"Recorte da placa salvo em: {save_path}")
            else:
                logging.warning(f"Coordenadas de recorte inválidas recebidas: {plate_bbox}")
        except Exception as e:
            logging.error(f"Falha ao recortar a imagem da placa: {e}")
            plate_image_filename = None

    # Tarefa 3: Cria o registro de "sighting" no banco de dados
    try:
        sighting_schema = schemas.VehicleSightingCreate(
            license_plate=plate_text,
            plate_image_url=plate_image_filename
        )
        # Passa o camera_id como um argumento separado para a função CRUD
        await crud.create_vehicle_sighting(db=db, sighting=sighting_schema, camera_id=camera_id)
        logging.info(f"Coletor registrou avistamento da placa: {plate_text} na câmera {camera_id}")
    except Exception as e:
        logging.error(f"Coletor: Falha ao salvar avistamento no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Falha ao processar o avistamento.")

    return {
        "message": "Evento LPR recebido e processado com sucesso.",
        "plate_image_saved": plate_image_filename is not None
    }