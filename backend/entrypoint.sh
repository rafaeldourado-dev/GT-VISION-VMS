#!/bin/bash

# Define a localização dos scripts de migração
MIGRATIONS_DIR="/code/migrations"

# 1. Verifica se a pasta de migrações existe. Se não, inicializa e configura o Alembic.
if [ ! -d "$MIGRATIONS_DIR" ]; then
  echo "Pasta de migrações não encontrada. A inicializar o Alembic..."
  alembic init migrations
  
  # 2. Configura o env.py para:
  #    - Encontrar os módulos da aplicação (app.models, etc.)
  #    - Ler a DATABASE_URL a partir das variáveis de ambiente
  #    - Apontar para os metadados dos seus modelos SQLAlchemy
  sed -i "s|from alembic import context|import sys\nfrom os.path import abspath, dirname\nsys.path.insert(0, dirname(dirname(abspath(__file__))))\n\nfrom alembic import context\nfrom app.config import settings|" /code/migrations/env.py
  sed -i "s|target_metadata = None|config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)\n\nfrom app.database import Base\nfrom app.models import *\ntarget_metadata = Base.metadata|" /code/migrations/env.py

  # 3. Gera o primeiro script de migração automaticamente
  echo "A gerar o primeiro script de migração..."
  alembic revision --autogenerate -m "Esquema inicial da base de dados"
fi

# 4. Aplica quaisquer migrações pendentes na base de dados
echo "A aplicar migrações da base de dados..."
alembic upgrade head

# 5. Inicia a aplicação principal
echo "A iniciar a aplicação FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000