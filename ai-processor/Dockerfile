# Usa uma imagem base do Pytorch que funciona bem em CPU
FROM python:3.11-slim

WORKDIR /code

# Instala dependências do sistema como OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Instala as dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o código do ai-processor para dentro do contentor
COPY . .

# --- INÍCIO DA MODIFICAÇÃO ---
# Cria a pasta para os modelos de IA e move o modelo genérico para lá
RUN mkdir -p models_ai
RUN cp yolov8n.pt models_ai/best.pt
# --- FIM DA MODIFICAÇÃO ---

# Comando para iniciar a aplicação 
CMD ["python", "main.py"]