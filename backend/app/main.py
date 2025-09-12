import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import SessionLocal
from . import models, schemas, crud
from .routers import auth, cameras, sightings, crm, dashboard, tickets, internal, streaming

app = FastAPI(
    title="GT-Vision API",
    description="API para a plataforma de videomonitoramento inteligente GT-Vision.",
    version="2.0.0"
)

# Permite que o frontend (rodando em localhost:5173) aceda ao backend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """
    Função de inicialização que cria um cliente e um utilizador admin padrão
    se eles não existirem.
    """
    async def create_defaults():
        async with SessionLocal() as db:
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
                    full_name="Admin User",
                    client_id=default_client.id,
                    role=models.UserRole.ADMIN
                )
                await crud.create_user(db, user=admin_in)
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(create_defaults())
    else:
        asyncio.run(create_defaults())

# Registra as rotas da API
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticação"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(sightings.router, prefix="/api/v1", tags=["Detecções"])
app.include_router(cameras.router, prefix="/api/v1", tags=["Câmeras"])
app.include_router(crm.router, prefix="/api/v1", tags=["CRM"])
app.include_router(tickets.router, prefix="/api/v1", tags=["Tickets"])
app.include_router(internal.router, prefix="/api/v1", tags=["Internal API"])

# A rota de streaming fica na raiz /ws
app.include_router(streaming.router)

@app.get("/api/health", status_code=200, tags=["Status"])
def health_check():
    """Verifica a saúde da API."""
    return {"status": "ok"}