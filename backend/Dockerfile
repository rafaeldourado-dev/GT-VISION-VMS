# Usa a imagem base do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contentor
WORKDIR /code

# Copia o ficheiro de dependências e instala-as
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o código do backend para o diretório de trabalho
COPY . .

# --- INÍCIO DA MODIFICAÇÃO ---
# Garante que o script de entrypoint tem permissão para ser executado
RUN chmod +x ./entrypoint.sh
# --- FIM DA MODIFICAÇÃO ---

# Define o entrypoint para o nosso script customizado
ENTRYPOINT ["./entrypoint.sh"]