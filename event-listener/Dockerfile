# Usa uma imagem Python leve como base
FROM python:3.9-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências para o contêiner
COPY requirements.txt .

# Instala as dependências listadas no requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do código (o listener.py) para o contêiner
COPY . .

# Comando que será executado quando o contêiner iniciar
CMD ["python", "listener.py"]