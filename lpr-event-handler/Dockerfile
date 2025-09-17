# Usa uma imagem base oficial do Python, leve e segura.
FROM python:3.10-slim

# Define o diretório de trabalho dentro do contentor.
WORKDIR /app

# Copia primeiro o ficheiro de requisitos para aproveitar o cache do Docker.
# O build só irá reinstalar as dependências se este ficheiro mudar.
COPY ./requirements.txt .

# Instala as dependências Python.
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação para dentro do contentor.
COPY ./app /app/app

# Expõe a porta que a aplicação vai usar para receber conexões.
EXPOSE 8080

# O comando para iniciar a aplicação quando o contentor arrancar.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]