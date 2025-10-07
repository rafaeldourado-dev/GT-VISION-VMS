import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- CUSTOM IMPORTS START ---
# Adiciona o diretório da aplicação ao path do sistema para permitir importações
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Importa os teus modelos e as configurações da aplicação
from app.models import Base
from app.config import settings
# --- CUSTOM IMPORTS END ---

# Este é o objeto de configuração do Alembic
config = context.config

# --- CORREÇÃO APLICADA AQUI ---
# Define o URL da base de dados no objeto de configuração do Alembic
# usando as configurações da sua aplicação, que carregam o .env corretamente.
# NOTA: O Alembic precisa de um driver síncrono como o psycopg2.
# A sua app usa asyncpg, então vamos substituir para a migração.
db_url = settings.DATABASE_URL_ASYNC.replace("postgresql+asyncpg", "postgresql+psycopg2")
config.set_main_option("sqlalchemy.url", db_url)
# --- FIM DA CORREÇÃO ---

# Interpreta o ficheiro de configuração para o logging do Python.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Adiciona os metadados do seu modelo para o suporte de 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executa as migrações em modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa as migrações em modo 'online'."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()