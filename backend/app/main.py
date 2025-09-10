from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
# Correção: Alterado 'AsyncSessionLocal' para 'SessionLocal' para corresponder a database.py
from .database import engine, Base, SessionLocal
from . import models, schemas, crud, dependencies
from .routers import auth, cameras, sightings, crm, dashboard, tickets


app = FastAPI(
    title="GT-Vision API",
    description="API para o sistema de reconhecimento de placas de veículos.",
    version="1.0.0"
)

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
async def on_startup():
    # Correção: Alterado 'AsyncSessionLocal' para 'SessionLocal'
    async with SessionLocal() as db:
        # Lógica para criar cliente e admin padrão
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

app.include_router(auth.router, prefix="/api/v1", tags=["Autenticação"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(sightings.router, prefix="/api/v1", tags=["Detecções"])
app.include_router(cameras.router, prefix="/api/v1", tags=["Câmeras"])
app.include_router(crm.router, prefix="/api/v1", tags=["CRM"])
app.include_router(tickets.router, prefix="/api/v1", tags=["Tickets"])

@app.get("/api/health", status_code=200, tags=["Status"])
def health_check():
    return {"status": "ok"}