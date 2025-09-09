from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Esta linha diz ao Pydantic para carregar as variáveis do seu ficheiro .env
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Variáveis que vêm diretamente do seu .env
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # Propriedade que constrói a URL da base de dados síncrona para o Alembic
    @property
    def DATABASE_URL(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    # Propriedade que constrói a URL da base de dados assíncrona
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

    # O resto das suas configurações
    SECRET_KEY: str
    ALGORITHM: str # Removido o valor padrão "HS268" para usar o do .env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin"
    RABBITMQ_DEFAULT_USER: str = "user"
    RABBITMQ_DEFAULT_PASS: str = "password"
    RABBITMQ_HOST: str = "gt-vision-rabbitmq"

# Instância única que será usada em toda a aplicação
settings = Settings()