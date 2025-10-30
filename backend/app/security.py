from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from . import crud, models, dependencies

# --- Configuração de Hashing de Senha ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Constantes de Token ---
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = 30 # Duração do refresh token
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY # Chave para access tokens
REFRESH_SECRET_KEY = settings.REFRESH_SECRET_KEY # Chave separada para refresh tokens

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- Funções de Access Token ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Funções de Refresh Token ---
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def refresh_access_token(token: str, db: AsyncSession):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials, please log in again",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    # Gera um novo access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return new_access_token

# --- Funções de Password Reset Token (BLOCO ADICIONADO) ---

# Chave separada para tokens de reset de senha para maior segurança
PASSWORD_RESET_SECRET_KEY = settings.SECRET_KEY + "_password_reset"
PASSWORD_RESET_EXPIRE_MINUTES = 60  # O token expira em 1 hora

def create_password_reset_token(email: str) -> str:
    """
    Cria um token JWT específico para reset de senha.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": email,
        "scope": "password_reset"  # Um 'scope' para garantir que ele só sirva para isso
    }
    encoded_jwt = jwt.encode(to_encode, PASSWORD_RESET_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verifica o token de reset de senha.
    Retorna o email se o token for válido e não expirado, senão None.
    """
    try:
        payload = jwt.decode(token, PASSWORD_RESET_SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verifica se o 'scope' do token é o correto
        if payload.get("scope") != "password_reset":
            return None
            
        email: str = payload.get("sub")
        if email is None:
            return None
        
        return email
        
    except JWTError:
        # Token inválido, expirado ou com assinatura errada
        return None
