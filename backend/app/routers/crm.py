from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, dependencies

router = APIRouter(tags=["CRM"])

# Dependência para obter o usuário atual (protege as rotas)
CurrentUser = Depends(dependencies.get_current_user)

@router.post("/clients/", response_model=schemas.Client)
def create_client(client: schemas.ClientCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = CurrentUser):
    return crud.create_client(db=db, client=client)

@router.get("/clients/", response_model=List[schemas.Client])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db), current_user: models.User = CurrentUser):
    clients = crud.get_clients(db, skip=skip, limit=limit)
    return clients

@router.get("/clients/{client_id}", response_model=schemas.Client)
def read_client(client_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = CurrentUser):
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client