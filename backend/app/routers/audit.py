from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from .. import crud, schemas, models
from ..dependencies import get_db, get_current_client_admin

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit"],
    dependencies=[Depends(get_current_client_admin)] # Apenas admins podem ver os logs
)

class PaginatedAuditLogs(schemas.BaseModel):
    items: List[schemas.AuditLog]
    total: int

@router.get("/", response_model=PaginatedAuditLogs)
async def read_audit_logs(
    skip: int = 0,
    limit: int = 100,
    actor_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_client_admin)
):
    """
    Retorna uma lista paginada de logs de auditoria para o cliente do administrador.
    """
    logs_data = await crud.get_audit_logs_by_client(
        db,
        client_id=current_user.client_id,
        skip=skip,
        limit=limit,
        actor_id=actor_id,
        action=action,
        start_date=start_date,
        end_date=end_date,
    )
    return logs_data