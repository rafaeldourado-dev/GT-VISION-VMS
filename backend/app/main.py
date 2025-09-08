from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import async_engine, Base, AsyncSessionLocal
from . import models, schemas, crud, dependencies
from .routers import auth, cameras, sightings, crm, dashboard

app = FastAPI(
    title="GT-Vision API",
    description="API para o sistema de reconhecimento de placas de veículos.",
    version="1.0.0"
)

# Configuração do CORS para permitir que o frontend acesse a API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

@app.on_event("startup")
async def on_startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        default_client = await crud.get_client_by_name(db, name="Default Client")
        if not default_client:
            client_in = schemas.ClientCreate(name="Default Client")
            default_client = await crud.create_client(db, client=client_in)
        
        admin_email = "admin@example.com"
        admin_user = await crud.get_user_by_email(db, email=admin_email)
        if not admin_user:
            admin_in = schemas.UserCreate(
                email=admin_email,
                password="adminpassword",
                client_id=default_client.id,
                role=models.UserRole.ADMIN 
            )
            await crud.create_user(db, user=admin_in)

# Inclusão dos routers
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticação"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(sightings.router, prefix="/api/v1", tags=["Detecções"])

auth_dependency = [Depends(dependencies.get_current_user)]
app.include_router(cameras.router, prefix="/api/v1", tags=["Câmeras"], dependencies=auth_dependency)
app.include_router(crm.router, prefix="/api/v1", tags=["CRM"], dependencies=auth_dependency)

@app.get("/api/health", status_code=200, tags=["Status"])
def health_check():
    """
    Endpoint para verificação de saúde do serviço.
    """
    return {"status": "ok"}