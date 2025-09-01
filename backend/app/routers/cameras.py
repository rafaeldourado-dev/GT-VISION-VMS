from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, dependencies

router = APIRouter(tags=["Cameras"])

# Dependência para proteger as rotas
CurrentUser = Depends(dependencies.get_current_user)

@router.post("/cameras/", response_model=schemas.Camera)
def create_camera(camera: schemas.CameraCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = CurrentUser):
    return crud.create_camera(db=db, camera=camera)

@router.get("/cameras/", response_model=List[schemas.Camera])
def read_cameras(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db), current_user: models.User = CurrentUser):
    cameras = crud.get_cameras(db, skip=skip, limit=limit)
    return cameras

# ROTA ADICIONADA PARA CORRIGIR O ERRO 404
@router.get("/cameras/service/active", response_model=List[schemas.Camera])
def read_active_cameras(db: Session = Depends(dependencies.get_db)):
    """
    Endpoint para o serviço de IA obter a lista de câmeras.
    Atualmente retorna todas as câmeras, pois não há status 'ativo'.
    """
    return crud.get_cameras(db, skip=0, limit=1000) # Retorna até 1000 câmeras

@router.get("/cameras/{camera_id}", response_model=schemas.Camera)
def read_camera(camera_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = CurrentUser):
    db_camera = crud.get_camera(db, camera_id=camera_id)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera