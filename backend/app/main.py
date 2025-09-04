from fastapi import FastAPI
from .database import async_engine, Base, AsyncSessionLocal
from . import models, schemas, crud
from .routers import auth, cameras, sightings, crm, dashboard

app = FastAPI(
    title="GT-Vision API",
    description="API para o sistema de reconhecimento de placas de veículos.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    """
    Cria as tabelas da base de dados, o cliente padrão e o utilizador admin ao iniciar.
    """
    # Cria as tabelas
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Garante que o cliente e o utilizador admin padrão existam
    async with AsyncSessionLocal() as db:
        # 1. Verificar/Criar cliente padrão
        default_client = await crud.get_client_by_name(db, name="Default Client")
        if not default_client:
            client_in = schemas.ClientCreate(name="Default Client")
            default_client = await crud.create_client(db, client=client_in)
        
        # 2. Verificar/Criar utilizador admin
        admin_email = "admin@example.com"
        admin_user = await crud.get_user_by_username(db, username=admin_email)
        if not admin_user:
            admin_in = schemas.UserCreate(
                email=admin_email,
                password="adminpassword", # Mudar isto para uma variável de ambiente em produção
                client_id=default_client.id,
                role=models.UserRole.ADMIN 
            )
            await crud.create_user(db, user=admin_in)


# Inclui os roteadores da aplicação
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["Câmeras"])
app.include_router(sightings.router, prefix="/api/sightings", tags=["Detecções"])
app.include_router(crm.router, prefix="/api/crm", tags=["CRM"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/api/health", status_code=200, tags=["Status"])
def health_check():
    """
    Endpoint para verificação de saúde do serviço.
    """
    return {"status": "ok"}