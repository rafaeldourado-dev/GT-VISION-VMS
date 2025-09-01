from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, dependencies

router = APIRouter(
    prefix="/crm",
    tags=["CRM"],
    dependencies=[Depends(dependencies.get_current_user)]
)

@router.post("/clients/", response_model=schemas.ClientSchema)
def create_client(client: schemas.ClientCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_client(db=db, client=client)

@router.get("/clients/", response_model=List[schemas.ClientSchema])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    clients = crud.get_clients(db, skip=skip, limit=limit)
    return clients