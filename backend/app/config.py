# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RABBITMQ_HOST: str = "rabbitmq" # Adicionada a variável do RabbitMQ

    class Config:
        env_file = ".env"

settings = Settings()