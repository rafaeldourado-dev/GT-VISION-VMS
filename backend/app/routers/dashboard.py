from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis # NOVO: Importa o cliente Redis
from .. import crud, schemas, dependencies, models

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Rota para estatísticas que agora usa o cache
@router.get("/stats/", response_model=schemas.DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
    redis_client: redis.Redis = Depends(dependencies.get_redis_client), # NOVO: Injeta o cliente Redis
):
    """Retorna estatísticas do dashboard para o cliente do usuário autenticado, usando Cache-Aside."""
    # Usa o client_id do utilizador autenticado, em vez de um valor fixo.
    stats = await crud.get_dashboard_stats(
        db, client_id=current_user.client_id, redis_client=redis_client # NOVO: Passa o cliente Redis
    )
    return stats