from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models, dependencies

router = APIRouter(prefix="/cameras", tags=["Cameras"])

@router.post("/", response_model=schemas.CameraSchema, dependencies=[Depends(dependencies.get_current_user)])
def create_camera_for_user(camera: schemas.CameraCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    return crud.create_camera(db=db, camera=camera, user_id=current_user.id)

@router.get("/", response_model=List[schemas.CameraSchema], dependencies=[Depends(dependencies.get_current_user)])
def read_cameras_for_user(db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    return crud.get_cameras_by_user(db=db, user_id=current_user.id)

@router.get("/service/active", response_model=List[schemas.CameraSchema], dependencies=[Depends(dependencies.get_service_user)])
def read_active_cameras_for_service(db: Session = Depends(dependencies.get_db)):
    return crud.get_all_active_cameras(db=db)