# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- CORREÇÃO AQUI ---
# Install system dependencies, INCLUDING curl for the healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client curl && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (sem o entrypoint.sh)
COPY ./alembic.ini /app/alembic.ini
COPY ./app /app/app
COPY ./migrations /app/migrations

# Cria o entrypoint.sh usando um "here document" para garantir a formatação correta
RUN cat <<EOF > /app/entrypoint.sh
#!/bin/sh
echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -p 5432 -q -U "\$POSTGRES_USER"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "PostgreSQL is up - executing command"
echo "Running database migrations..."
alembic upgrade head
echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF

# Torna o script executável
RUN chmod +x /app/entrypoint.sh

# Cria o diretório para capturas
RUN mkdir -p /app/captures

# O comando para rodar a aplicação
CMD ["sh", "/app/entrypoint.sh"]