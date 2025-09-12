from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# --- CORREÇÃO APLICADA AQUI ---
from ..dependencies import get_db, get_current_user
# -----------------------------
from .. import crud, schemas, models

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
    dependencies=[Depends(get_current_user)], 
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Ticket, status_code=201)
async def create_new_ticket(
    ticket: schemas.TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user) 
):
    """Cria um novo ticket de suporte para o usuário autenticado."""
    return await crud.create_ticket(db=db, ticket=ticket, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Ticket])
async def read_user_tickets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user) 
):
    """Retorna uma lista de tickets pertencentes ao usuário autenticado."""
    tickets = await crud.get_tickets_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return tickets

@router.get("/{ticket_id}", response_model=schemas.Ticket)
async def read_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Retorna um ticket específico do usuário autenticado."""
    ticket = await crud.get_ticket_by_id(db, ticket_id=ticket_id)
    if not ticket or ticket.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    return ticket

@router.put("/{ticket_id}", response_model=schemas.Ticket)
async def update_ticket(
    ticket_id: int,
    ticket_data: schemas.TicketUpdate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza um ticket do usuário autenticado."""
    ticket = await crud.get_ticket_by_id(db, ticket_id=ticket_id)
    if not ticket or ticket.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    return await crud.update_ticket(db, ticket_id=ticket_id, ticket_update=ticket_data)

@router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Exclui um ticket do usuário autenticado."""
    ticket = await crud.get_ticket_by_id(db, ticket_id=ticket_id)
    if not ticket or ticket.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    await crud.delete_ticket(db, ticket_id=ticket_id)
    return None