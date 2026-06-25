"""edit job status lagi

Revision ID: eb4815a9a077
Revises: 626a396c2b2f
Create Date: 2026-05-22 01:40:11.458999
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'eb4815a9a077'
down_revision: Union[str, Sequence[str], None] = '626a396c2b2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        'check_job_status',
        'jobs',
        type_='check'
    )

    op.create_check_constraint(
        'check_job_status',
        'jobs',
        "status IN ('PENDING', 'QUEUE', 'RUNNING', 'COMPLETED', 'MODIFIED', 'ERROR')"
    )


def downgrade() -> None:
    op.drop_constraint(
        'check_job_status',
        'jobs',
        type_='check'
    )

    op.create_check_constraint(
        'check_job_status',
        'jobs',
        "status IN ('PENDING', 'RUNNING', 'SUCCESS')"
    )