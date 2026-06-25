"""add default null in comparison

Revision ID: d088357813eb
Revises: bcc4ef739baa
Create Date: 2026-04-22 22:34:06.643484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd088357813eb'
down_revision: Union[str, Sequence[str], None] = 'bcc4ef739baa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
