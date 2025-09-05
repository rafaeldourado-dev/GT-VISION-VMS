from fastapi import FastAPI, Depends
from .database import async_engine, Base, AsyncSessionLocal
from . import models, schemas, crud, dependencies
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


# --- CORREÇÃO: Padronizando todos os prefixos para /api/v1 ---

# O router de autenticação não precisa de dependências
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticação"])

# Os outros routers precisam da dependência de autenticação
auth_dependency = [Depends(dependencies.get_current_user)]

app.include_router(cameras.router, prefix="/api/v1", tags=["Câmeras"], dependencies=auth_dependency)
app.include_router(sightings.router, prefix="/api/v1", tags=["Detecções"], dependencies=auth_dependency)
app.include_router(crm.router, prefix="/api/v1", tags=["CRM"], dependencies=auth_dependency)
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"], dependencies=auth_dependency)


@app.get("/api/health", status_code=200, tags=["Status"])
def health_check():
    """
    Endpoint para verificação de saúde do serviço.
    """
    return {"status": "ok"}
