import os
from logging.config import fileConfig

# Importe 'create_engine' para criar a conexão manualmente
from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

# Importe os seus modelos e configurações
from app.models import Base
from app.config import settings

# Carregue a configuração do Alembic
config = context.config

# Se houver um ficheiro de configuração, carregue-o
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- CORREÇÃO DEFINITIVA AQUI ---
# 1. Crie uma versão "segura" da URL para o parser de configuração do Alembic
#    substituindo '%' por '%%'. Isto resolve o ValueError.
safe_database_url = settings.DATABASE_URL.replace('%', '%%')
config.set_main_option('sqlalchemy.url', safe_database_url)

# Defina os metadados do seu modelo
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executa migrações em modo 'offline'."""
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
    """Executa migrações em modo 'online'."""
    # 2. Crie a conexão (engine) usando a URL ORIGINAL de 'settings'.
    #    A biblioteca SQLAlchemy/psycopg2 sabe como lidar com a URL corretamente.
    connectable = create_engine(
        settings.DATABASE_URL,
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