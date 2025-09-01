from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas, dependencies

router = APIRouter(prefix="/sightings", tags=["Sightings"])

@router.post("/", response_model=schemas.VehicleSightingSchema, dependencies=[Depends(dependencies.get_service_user)])
def create_sighting_from_service(sighting: schemas.VehicleSightingCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_sighting(db=db, sighting_data=sighting.model_dump())