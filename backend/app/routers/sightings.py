from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, dependencies, models

router = APIRouter(tags=["Sightings"])

@router.post("/", response_model=schemas.Sighting, dependencies=[Depends(dependencies.get_service_user)])
def create_sighting(sighting: schemas.SightingCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_sighting(db=db, sighting=sighting)

@router.get("/", response_model=List[schemas.Sighting], dependencies=[Depends(dependencies.get_current_user)])
def read_sightings(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    sightings = crud.get_sightings(db, skip=skip, limit=limit)
    return sightings