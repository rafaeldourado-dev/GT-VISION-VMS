from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .. import crud, schemas, models, security
from ..dependencies import get_db, get_current_client_admin, get_current_active_user

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_client_admin)] # Protege todas as rotas
)

@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT,
            # Esta rota usa uma dependência diferente para não ser bloqueada
            dependencies=[Depends(get_current_active_user)])
async def update_own_password(
    password_data: schemas.UserSelfPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Permite que o usuário logado altere sua própria senha.
    """
    # Verifica a senha atual
    if not security.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )
    
    # Atualiza para a nova senha
    await crud.update_own_password(db=db, user=current_user, new_password=password_data.new_password)
    return


@router.get("/", response_model=List[schemas.User])
async def read_users_for_client(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_client_admin)
):
    """
    Retorna uma lista de todos os usuários associados ao mesmo cliente que o admin logado.
    """
    users = await crud.get_users_by_client(db, client_id=current_user.client_id)
    return users

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user_for_client(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_client_admin)
):
    """
    Cria um novo usuário para o cliente do admin logado.
    """
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    # Força o novo usuário a pertencer ao mesmo cliente do admin
    user.client_id = current_user.client_id
    new_user = await crud.create_user(db=db, user=user)

    # NOVO: Registrar no log de auditoria
    await crud.create_audit_log(
        db, actor_id=current_user.id, action="USER_CREATED",
        target_id=new_user.id, target_type="User",
        details=f"Usuário '{new_user.email}' criado por '{current_user.email}'."
    )
    return new_user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user_details(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_client_admin)
):
    """
    Atualiza os detalhes de um usuário.
    """
    db_user = await crud.get_user(db, user_id=user_id)
    if not db_user or db_user.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return await crud.update_user(db=db, user=db_user, user_update=user_update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_from_client(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_client_admin)
):
    """
    Deleta um usuário.
    """
    db_user = await crud.get_user(db, user_id=user_id)
    if not db_user or db_user.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Não é permitido se auto-deletar")

    await crud.delete_user(db=db, user_id=user_id)
    return

@router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_user_password(
    user_id: int,
    password_data: schemas.UserPasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_client_admin)
):
    """
    Redefine a senha de um usuário. Apenas administradores podem fazer isso
    para usuários dentro do seu próprio cliente.
    """
    db_user = await crud.get_user(db, user_id=user_id)
    if not db_user or db_user.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Não é permitido redefinir a própria senha por esta rota.")

    updated_user = await crud.update_user_password(db=db, user=db_user, new_password=password_data.new_password)

    # NOVO: Registrar no log de auditoria
    await crud.create_audit_log(
        db, actor_id=current_user.id, action="PASSWORD_RESET",
        target_id=updated_user.id, target_type="User",
        details=f"Senha do usuário '{updated_user.email}' redefinida por '{current_user.email}'."
    )
    return
