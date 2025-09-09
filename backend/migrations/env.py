import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Importa a base do teu modelo para que as tabelas sejam detetadas
# e as settings para obter a URL da base de dados.
from app.models import Base
from app.config import settings

# este é o objeto de configuração do Alembic, que fornece
# acesso aos valores no ficheiro .ini.
config = context.config

# Interpreta o ficheiro de configuração para o logging do Python.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define a URL da base de dados a partir das tuas settings.
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

# Adiciona o teu modelo de metadados aqui para o 'autogenerate'
# ter suporte.
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    # --- CORREÇÃO APLICADA AQUI ---
    connectable = engine_from_config(
        config.get_section(config.config_ini_section), # <-- 'main_section' foi corrigido para 'config_ini_section'
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