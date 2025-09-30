from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# O ficheiro do banco de dados será criado na raiz do ai-processor
SQLALCHEMY_DATABASE_URL = "sqlite:///./aiprocessor.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Necessário para SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função para criar o banco de dados e as tabelas
def init_db():
    Base.metadata.create_all(bind=engine)