"""Update relation document and comparison

Revision ID: 66eee606cc3f
Revises: 4fd5b58d92df
Create Date: 2026-05-13 10:34:20.663068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66eee606cc3f'
down_revision: Union[str, Sequence[str], None] = '4fd5b58d92df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
