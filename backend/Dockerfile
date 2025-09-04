# Use a imagem base apropriada para sua aplicação (ex: python:3.10-slim)
FROM python:3.10-slim

# --- CORREÇÃO AQUI: Adicionado 'curl' à lista de instalação ---
# Instala o cliente do PostgreSQL, dos2unix e o curl para o healthcheck
RUN apt-get update && apt-get install -y postgresql-client dos2unix curl && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos de dependências
COPY ./requirements.txt /app/requirements.txt

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da sua aplicação
COPY . /app

# Copia o script de entrypoint e corrige seu formato de quebra de linha
COPY ./entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/entrypoint.sh

# Torna o script de entrypoint executável
RUN chmod +x /app/entrypoint.sh

# Define o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# O comando a ser executado pelo entrypoint (CMD)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]