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
# Aumenta o atraso para garantir que a transação de migração seja aplicada no DB e o pool de conexões da aplicação reconheça a nova tabela.
echo "Waiting for database schema to stabilize..."
sleep 10 # Aumentado de 3s para 10s para resolver o race condition
# ---------------------

# Inicia a aplicação com a flag --reload para desenvolvimento
echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload