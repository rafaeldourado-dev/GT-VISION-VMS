from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app import crud, schemas, models # Added models
from app.dependencies import get_db, get_current_active_user # Added get_current_active_user
from app.security import (
    create_access_token, 
    get_password_hash, # Added for password reset
    verify_password,
    create_password_reset_token,
    verify_password_reset_token
)
from app.utils.email import send_reset_password_email # Added for password reset

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Handles user login and returns a JWT token.
    This is the endpoint that was causing the 404.
    """
    user = await crud.get_user_by_email(db, email=form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )


    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value, "client_id": str(user.client_id)}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """Retorna o usuário autenticado atual."""
    return current_user

@router.post("/request-password-reset")
async def request_password_reset(
    email_data: schemas.PasswordResetRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a password reset token and sends it via email.
    """
    user = await crud.get_user_by_email(db, email=email_data.email)
    if not user:
        # We don't want to reveal if a user exists or not
        return {"msg": "If an account with this email exists, a password reset link has been sent."}

    reset_token = create_password_reset_token(email=user.email)
    await send_reset_password_email(email_to=user.email, token=reset_token)
    
    return {"msg": "If an account with this email exists, a password reset link has been sent."}

@router.post("/reset-password", response_model=schemas.User)
async def reset_password(
    token_data: schemas.PasswordReset, 
    db: AsyncSession = Depends(get_db)
):
    """
    Verifies the password reset token and updates the user's password.
    """
    email = verify_password_reset_token(token_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    user = await crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    hashed_password = get_password_hash(token_data.new_password)
    user.hashed_password = hashed_password
    # --- CORREÇÃO AQUI ---
    user.password_change_required = False  # Reset the flag
    # ---------------------
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

@router.post("/force-password-change", response_model=schemas.User)
async def force_password_change(
    password_data: schemas.PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Troca de senha autenticada (usuário já logado)."""
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    hashed_password = get_password_hash(password_data.new_password)
    current_user.hashed_password = hashed_password
    current_user.password_change_required = False
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.post("/force-password-change-initial", response_model=schemas.User)
async def force_password_change_initial(
    data: schemas.ForcedPasswordChange,
    db: AsyncSession = Depends(get_db)
):
    """Permite a troca de senha sem JWT no primeiro login (com email + senha antiga)."""
    user = await crud.get_user_by_email(db, email=data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")
    if not user.password_change_required:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password change not required")
    user.hashed_password = get_password_hash(data.new_password)
    user.password_change_required = False
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user