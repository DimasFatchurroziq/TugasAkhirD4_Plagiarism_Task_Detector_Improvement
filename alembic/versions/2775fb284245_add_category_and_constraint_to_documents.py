"""add_category_and_constraint_to_documents

Revision ID: 2775fb284245
Revises: 95ce2d4c50cd
Create Date: 2026-06-23 00:57:42.744808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2775fb284245'
down_revision: Union[str, Sequence[str], None] = '95ce2d4c50cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tambah kolom 'category' terlebih dahulu
    op.add_column('documents', sa.Column('category', sa.String(length=10), nullable=True))
    
    # 2. Tambah CheckConstraint secara eksplisit
    op.create_check_constraint(
        'check_document_category',
        'documents',
        "category IN ('ONE', 'MANY')"
    )

def downgrade() -> None:
    # 1. Hapus CheckConstraint terlebih dahulu
    op.drop_constraint('check_document_category', 'documents', type_='check')
    
    # 2. Hapus kolom 'category'
    op.drop_column('documents', 'category')
