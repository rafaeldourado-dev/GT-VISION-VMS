# backend/Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y postgresql-client dos2unix curl && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./alembic.ini /app/alembic.ini
COPY ./app /app/app
COPY ./migrations /app/migrations
COPY ./entrypoint.sh /app/entrypoint.sh

# --- CORREÇÃO AQUI ---
# 1. Torna o script executável
RUN chmod +x /app/entrypoint.sh
# 2. Corrige o formato de quebra de linha (bom para evitar problemas entre Windows/Linux)
RUN dos2unix /app/entrypoint.sh
# --------------------

# Cria a diretoria para capturas
RUN mkdir -p /app/captures

# The command to run the application
CMD ["/app/entrypoint.sh"]