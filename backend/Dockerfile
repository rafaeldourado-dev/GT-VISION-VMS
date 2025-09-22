# Use a imagem base apropriada para sua aplicação (ex: python:3.10-slim)
FROM python:3.10-slim

# Instala o cliente do PostgreSQL, dos2unix e o curl para o healthcheck
RUN apt-get update && apt-get install -y postgresql-client dos2unix curl && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos de dependências primeiro para aproveitar o cache
COPY ./requirements.txt /app/requirements.txt

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# --- Copia o código da aplicação de forma explícita ---
COPY ./alembic.ini /app/alembic.ini
COPY ./app /app/app
COPY ./migrations /app/migrations

# --- CORREÇÃO APLICADA AQUI ---
# Copia o script de entrypoint e JÁ APLICA AS PERMISSÕES E CORREÇÕES
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh      # 1. Torna o script executável
RUN dos2unix /app/entrypoint.sh      # 2. Corrige o formato de quebra de linha

# Cria o diretório de capturas para que ele exista no container
RUN mkdir -p /app/captures

# A instrução para iniciar o container (ENTRYPOINT ou CMD) deve vir por último.
# Se seu entrypoint.sh já está no repositório, garanta que essa linha exista no final.
# ENTRYPOINT ["/app/entrypoint.sh"]
