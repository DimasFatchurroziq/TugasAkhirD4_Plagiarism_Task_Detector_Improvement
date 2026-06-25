"""add default null in comparison

Revision ID: bcc4ef739baa
Revises: 2f7b8484f816
Create Date: 2026-04-22 22:31:31.808654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcc4ef739baa'
down_revision: Union[str, Sequence[str], None] = '2f7b8484f816'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
