from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas, models
from .database import SessionLocal # <-- CORRIGIDO AQUI
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db: # <-- CORRIGIDO AQUI
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