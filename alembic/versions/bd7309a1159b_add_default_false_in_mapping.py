"""add default false in mapping

Revision ID: bd7309a1159b
Revises: d088357813eb
Create Date: 2026-04-23 00:07:51.284589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd7309a1159b'
down_revision: Union[str, Sequence[str], None] = 'd088357813eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
