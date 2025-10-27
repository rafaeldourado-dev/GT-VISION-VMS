import asyncio
import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from sqlalchemy.exc import ProgrammingError, DBAPIError
# from typing import List # REMOVIDO: Não é mais necessário aqui
from sqlalchemy.ext.asyncio import AsyncSession # Adicionado import AsyncSession que faltava no seu ficheiro original para SessionLocal funcionar

from .config import settings
from .database import SessionLocal # Usar SessionLocal
from . import models, schemas, crud
from .routers import auth, cameras, sightings, crm, dashboard, tickets, internal, streaming, users, blacklist, notifications, audit
# from .routers.streaming import start_stream_proxy # REMOVIDO: Import não existe mais no streaming.py antigo

app = FastAPI(
    title="GT-Vision API",
    description="API para a plataforma de videomonitoramento inteligente GT-Vision.",
    version="2.0.0"
)

# Define o caminho para a diretoria de capturas
CAPTURES_DIR = Path("captures")
# Cria a diretoria se ela não existir
os.makedirs(CAPTURES_DIR, exist_ok=True)

# Monta a diretoria de ficheiros estáticos (agora com a certeza de que ela existe)
app.mount(f"/{CAPTURES_DIR}", StaticFiles(directory=CAPTURES_DIR), name=str(CAPTURES_DIR))


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
    (A lógica de iniciar proxies foi removida)
    """
    async def create_defaults():
        # --- LÓGICA DE INICIALIZAÇÃO ROBUSTA (O seu código original, mantido) ---
        max_retries = 10
        for attempt in range(max_retries):
            try:
                # Uma nova sessão é criada para cada tentativa
                async with SessionLocal() as db:
                    # Cria/obtém o cliente padrão
                    default_client = await crud.get_client_by_name(db, name="Default Client")
                    if not default_client:
                        client_in = schemas.ClientCreate(name="Default Client")
                        default_client = await crud.create_client(db, client=client_in)

                    # Cria/obtém o utilizador admin
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

                    # Cria/valida a chave de API interna
                    ai_processor_api_key = await crud.validate_api_key(db, settings.ADMIN_API_KEY)
                    if not ai_processor_api_key:
                        api_key_in = schemas.ApiKeyCreate(
                            key=settings.ADMIN_API_KEY,
                            name="AI Processor Internal Key",
                            client_id=default_client.id
                        )
                        await crud.create_api_key(db, api_key=api_key_in)

                    logging.info("Inicialização de dados padrão (cliente, admin, chave de API) concluída com sucesso.")
                    break  # Sai do loop se tudo correr bem

            except (ProgrammingError, DBAPIError) as e:
                error_message = str(e)
                is_retryable_error = any(msg in error_message for msg in [
                    'relation "clients" does not exist',
                    'relation "users" does not exist',
                    'relation "api_keys" does not exist',
                    'current transaction is aborted'
                ])

                if is_retryable_error and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logging.warning(f"Erro de banco de dados na inicialização ({type(e).__name__}). Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logging.error(f"Erro fatal de banco de dados na inicialização após {max_retries} tentativas: {e}")
                    raise

    # REMOVIDO: A função start_active_camera_proxies foi removida daqui

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(create_defaults())
        # REMOVIDO: A chamada loop.create_task(start_active_camera_proxies()) foi removida
    else:
        asyncio.run(create_defaults())
        # REMOVIDO: A chamada asyncio.run(start_active_camera_proxies()) foi removida

# Registra as rotas da API
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticação"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(sightings.router, prefix="/api/v1", tags=["Detecções"])
app.include_router(cameras.router, prefix="/api/v1", tags=["Câmeras"])
app.include_router(crm.router, prefix="/api/v1", tags=["CRM"])
app.include_router(blacklist.router, prefix="/api/v1", tags=["Blacklist"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(tickets.router, prefix="/api/v1", tags=["Tickets"])
app.include_router(audit.router, prefix="/api/v1", tags=["Audit"])
app.include_router(internal.router, prefix="/api/v1", tags=["Internal API"])
app.include_router(notifications.router) # Rota de notificações WebSocket (prefixo /ws)
# CORRIGIDO: O prefixo /api/v1 foi removido daqui para usar o prefixo /ws do router antigo
app.include_router(streaming.router)

@app.get("/api/health", status_code=200, tags=["Status"])
def health_check():
    """Verifica a saúde da API."""
    return {"status": "ok"}