#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

# Usa pg_isready para verificar se a base de dados está pronta
while ! pg_isready -h db -p 5432 -q -U "$POSTGRES_USER"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"

# Executa as migrações da base de dados
echo "Running database migrations..."
alembic upgrade head

# --- CORREÇÃO AQUI ---
# Inicia a aplicação com a flag --reload para desenvolvimento
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload