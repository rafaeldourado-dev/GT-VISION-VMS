# backend/migrations/versions/101e3201824f_....py - VERSÃO CORRIGIDA

"""adiciona a coluna camera_type a tabela cameras

Revision ID: 101e3201824f
Revises: 1d7135f69bde
Create Date: 2025-10-06 09:22:04.123456 
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql # Importar o dialeto postgresql

# revision identifiers, used by Alembic.
revision: str = '101e3201824f'
down_revision: Union[str, Sequence[str], None] = '1d7135f69bde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Definir o tipo ENUM fora das funções para ser reutilizável
camera_type_enum = sa.Enum('GENERIC_RTSP', 'INTELBRAS_PUSH', name='cameratype')

def upgrade() -> None:
    """Upgrade schema."""
    # --- CORREÇÃO AQUI ---
    # Passo 1: Criar o tipo ENUM 'cameratype' no PostgreSQL
    op.execute("CREATE TYPE cameratype AS ENUM ('GENERIC_RTSP', 'INTELBRAS_PUSH')")
    
    # Passo 2: Adicionar a coluna à tabela 'cameras', agora usando o tipo que acabou de ser criado.
    # Usamos o tipo `postgresql.ENUM` para que o Alembic saiba como lidar com ele.
    op.add_column('cameras', sa.Column('camera_type', postgresql.ENUM('GENERIC_RTSP', 'INTELBRAS_PUSH', name='cameratype'), nullable=False, server_default='GENERIC_RTSP'))
    # Adicionamos um server_default para evitar problemas com linhas existentes.

def downgrade() -> None:
    """Downgrade schema."""
    # --- CORREÇÃO AQUI ---
    # A ordem inversa: primeiro remove a coluna, depois apaga o tipo.
    op.drop_column('cameras', 'camera_type')
    op.execute("DROP TYPE cameratype")