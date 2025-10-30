from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # NOVO: Configurações do Redis
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_CACHE_TTL_SECONDS: int = 300 # Padrão de 5 minutos

    # Configurações do RabbitMQ
    RABBITMQ_HOST: str

    # NOVO: Credenciais para a API do MediaMTX
    MEDIA_SERVER_API_USER: Optional[str] = None
    MEDIA_SERVER_API_PASS: Optional[str] = None

    # NOVO: Host público para o Media Server (acessível pelo browser do cliente)
    MEDIA_SERVER_PUBLIC_HOST: str = "localhost"


    @property
    def DATABASE_URL(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=f"{self.POSTGRES_DB}"
            )
        )

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=f"{self.POSTGRES_DB}"
            )
        )

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ADMIN_API_KEY: str
    
    # --- CORREÇÕES ADICIONADAS AQUI ---

    # 1. Chave do erro anterior
    REFRESH_SECRET_KEY: str 

    # 2. Chave do erro atual (para cookies seguros)
    ENVIRONMENT: str = "development" # Padrão 'development' se não estiver no .env

    # 3. Credenciais do Gestor Master (para remover do main.py)
    GESTOR_MASTER_CLIENT_NAME: str
    GESTOR_DEFAULT_EMAIL: str
    GESTOR_DEFAULT_FULL_NAME: str
    GESTOR_DEFAULT_PASSWORD: str

settings = Settings()
# ------------------------------------