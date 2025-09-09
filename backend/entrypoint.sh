#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

# --- CORREÇÃO AQUI: Usa pg_isready em vez de nc ---
# As variáveis de ambiente (PGUSER, PGDATABASE, etc.) são lidas a partir do ficheiro .env
while ! pg_isready -h db -p 5432 -q -U "$POSTGRES_USER"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"

# Executa as migrações da base de dados
echo "Running database migrations..."
alembic upgrade head

# Inicia a aplicação (o CMD do Dockerfile)
exec "$@"