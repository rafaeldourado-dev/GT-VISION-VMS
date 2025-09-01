from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import SessionLocal
from . import crud, schemas, models
from .routers import auth, cameras, sightings, crm

# A linha Base.metadata.create_all(bind=engine) FOI REMOVIDA.

app = FastAPI(title="GT-Vision SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        admin_user = crud.get_user_by_email(db, email="admin@gtvision.com")
        if not admin_user:
            admin_in = schemas.UserCreate(email="admin@gtvision.com", password="admin_password_super_secret")
            user = crud.create_user(db, user=admin_in)
            user.role = models.UserRole.ADMIN
            crud.regenerate_user_api_key(db, user=user)
            db.commit()
    finally:
        db.close()

app.include_router(auth.router)
app.include_router(cameras.router)
app.include_router(sightings.router)
app.include_router(crm.router)

@app.get("/")
def read_root():
    return {"status": "API is running"}