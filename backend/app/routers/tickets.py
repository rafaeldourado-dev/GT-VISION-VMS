from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

# A importação foi corrigida aqui para usar 'get_current_user'
from ..dependencies import get_db, get_current_user 

from .. import crud, models, schemas

router = APIRouter(
    prefix="/api/v1/tickets",
    tags=["tickets"],
    dependencies=[Depends(get_current_user)], # Corrigido aqui
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Ticket, status_code=201)
async def create_new_ticket(
    ticket: schemas.TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Corrigido aqui
):
    """Cria um novo ticket de suporte para o usuário autenticado."""
    return await crud.create_ticket(db=db, ticket=ticket, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Ticket])
async def read_user_tickets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Corrigido aqui
):
    """Retorna uma lista de tickets pertencentes ao usuário autenticado."""
    tickets = await crud.get_tickets_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return tickets