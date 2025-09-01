from fastapi import FastAPI
from contextlib import asynccontextmanager
from . import models, crud, schemas
from .database import engine, SessionLocal
from .routers import auth, cameras, sightings, crm

# Cria as tabelas no banco de dados (se não existirem)
models.Base.metadata.create_all(bind=engine)

# Função de inicialização para criar o usuário admin
def startup_event():
    db = SessionLocal()
    try:
        # Verifica se o usuário administrador já existe
        admin_user = crud.get_user_by_email(db, email="admin@gtvision.com")
        if not admin_user:
            # Se não existir, cria um
            user_in = schemas.UserCreate(email="admin@gtvision.com", password="adminpassword")
            crud.create_user(db=db, user=user_in)
            print("Usuário administrador criado com sucesso.")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa a lógica de inicialização
    startup_event()
    yield
    # Lógica de encerramento (se houver) pode vir aqui

app = FastAPI(lifespan=lifespan)

# Inclui os roteadores da API
app.include_router(auth.router, prefix="/api")
app.include_router(cameras.router, prefix="/api")
app.include_router(sightings.router, prefix="/api")
app.include_router(crm.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API GT-Vision"}