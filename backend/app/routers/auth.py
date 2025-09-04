from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from .. import crud, schemas, security, dependencies, models

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(dependencies.get_db),
):
    user = await crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register/client", response_model=schemas.Client)
async def register_client(
    client: schemas.ClientCreate, db: AsyncSession = Depends(dependencies.get_db)
):
    # Lógica para verificar se o cliente já existe pode ser adicionada aqui
    return await crud.create_client(db=db, client=client)


@router.post("/register/user", response_model=schemas.User)
async def register_user(
    user: schemas.UserCreate, db: AsyncSession = Depends(dependencies.get_db)
):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Verifica se o Client existe
    db_client = await crud.get_client(db, client_id=user.client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    return await crud.create_user(db=db, user=user)

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(dependencies.get_current_user)):
    return current_user