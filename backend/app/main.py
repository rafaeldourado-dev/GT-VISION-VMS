import asyncio
import os
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

# Ajuste os imports para o caminho relativo correto dentro do seu projeto
from .database import SessionLocal
from . import models, schemas, crud
from .routers import auth, cameras, sightings, crm, dashboard, tickets, internal, streaming, coletor

app = FastAPI(
    title="GT-Vision API",
    description="API para a plataforma de videomonitoramento inteligente GT-Vision.",
    version="2.0.0"
)

# --- DIRETÓRIO DE CAPTURAS E ARQUIVOS ESTÁTICOS ---
CAPTURES_DIR = "/app/captures"
os.makedirs(CAPTURES_DIR, exist_ok=True)
app.mount("/api/v1/captures", StaticFiles(directory=CAPTURES_DIR), name="captures")

# --- CONFIGURAÇÃO DE CORS DINÂMICA ---
# As origens permitidas são lidas da variável de ambiente.
origins_str = os.getenv("BACKEND_CORS_ORIGINS", '["http://localhost:5173", "http://127.0.0.1:5173"]')
try:
    origins = json.loads(origins_str)
except json.JSONDecodeError:
    print("AVISO: Falha ao decodificar BACKEND_CORS_ORIGINS. Usando valor padrão.")
    origins = ["http://localhost:5173", "http://127.0.0.1:5173"]


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

            admin_email = os.getenv("ADMIN_DEFAULT_EMAIL", "admin@example.com")
            admin_user = await crud.get_user_by_email(db, email=admin_email)
            if not admin_user:
                admin_password = os.getenv("ADMIN_DEFAULT_PASSWORD", "adminpassword")
                if admin_password == "adminpassword":
                    print("\033[91mAVISO DE SEGURANÇA:\033[0m A usar senha padrão para o utilizador admin. Defina a variável de ambiente ADMIN_DEFAULT_PASSWORD em produção!")

                admin_in = schemas.UserCreate(
                    email=admin_email,
                    password=admin_password,
                    full_name="Admin User",
                    client_id=default_client.id,
                    role=models.UserRole.ADMIN
                )
                await crud.create_user(db, user=admin_in)

    # Lógica para garantir que a criação de defaults rode corretamente
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
app.include_router(coletor.router, prefix="/api/v1", tags=["Coletor de Eventos"])

# A rota de streaming fica na raiz /ws
app.include_router(streaming.router)

@app.get("/api/health", status_code=200, tags=["Status"])
def health_check():
    """Verifica a saúde da API."""
    return {"status": "ok"}