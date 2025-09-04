from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, dependencies

router = APIRouter(prefix="/crm", tags=["crm"])

@router.post("/leads", response_model=schemas.Lead)
async def create_new_lead(
    lead: schemas.LeadCreate,
    db: AsyncSession = Depends(dependencies.get_db),
    # Acesso a este endpoint deve ser restrito a admins no futuro
):
    return await crud.create_lead(db=db, lead=lead)

@router.get("/leads", response_model=List[schemas.Lead])
async def read_all_leads(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(dependencies.get_db),
    # Acesso a este endpoint deve ser restrito a admins no futuro
):
    leads = await crud.get_leads(db, skip=skip, limit=limit)
    return leads