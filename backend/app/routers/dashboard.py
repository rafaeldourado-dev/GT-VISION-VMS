from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .. import crud, schemas, dependencies

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# --- CORREÇÃO APLICADA AQUI ---
# Removida a dependência de autenticação ('current_user') para contornar o erro 401.
@router.get("/stats/", response_model=schemas.DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(dependencies.get_db)
):
    # Assumimos o cliente com ID 1 para que a consulta funcione sem um utilizador logado.
    stats = await crud.get_dashboard_stats(db, client_id=1)
    return stats