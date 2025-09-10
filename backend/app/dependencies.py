from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

# Estas são as importações corretas que o arquivo precisa
from . import crud, schemas, models
from .database import SessionLocal
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token") # Corrigido para o URL completo do token

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = await crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# Nova função de dependência para verificar se o usuário é um administrador de cliente ou superior
async def get_current_client_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.CLIENT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted for this user role",
        )
    return current_user