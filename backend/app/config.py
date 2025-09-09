from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # --- CORREÇÃO PRINCIPAL AQUI ---
    # Adiciona uma propriedade para a URL SÍNCRONA, que o Alembic precisa
    @property
    def DATABASE_URL(self) -> str:
        return str(
            PostgresDsn.build(
                # Usa o driver padrão do postgresql (síncrono)
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )
    # --- FIM DA CORREÇÃO ---

    # Propriedade que constrói a URL da base de dados assíncrona (para a App)
    @property
    def DATABASE_URL_ASYNC(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS268"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin"
    RABBITMQ_DEFAULT_USER: str = "user"
    RABBITMQ_DEFAULT_PASS: str = "password"
    RABBITMQ_HOST: str = "gt-vision-rabbitmq"

settings = Settings()