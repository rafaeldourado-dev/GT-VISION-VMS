#!/bin/bash

# Define as variáveis de ambiente com valores padrão (opcional, mas bom para depuração)
DB_HOST=${DB_HOST:-gt-vision-db}
DB_PORT=${DB_PORT:-5432}
DB_USER=${POSTGRES_USER:-user} # Certifique-se que POSTGRES_USER está sendo passado

# Espere o PostgreSQL estar pronto para aceitar conexões
echo "Aguardando o banco de dados em ${DB_HOST}:${DB_PORT} ficar pronto..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q -U "$DB_USER"; do
  echo "Banco de dados indisponível - aguardando..."
  sleep 2
done
echo "Banco de dados pronto!"

# Aplica as migrações do Alembic
echo "Aplicando migrações do banco de dados..."
alembic upgrade head

# Inicia a aplicação FastAPI com Uvicorn
echo "Iniciando o servidor da API..."
# O exec "$@" executa o comando passado como CMD no Dockerfile
exec "$@"
