"""drop alerts value

Revision ID: 5b0e3c9d7a21
Revises: f991ffaa5134
Create Date: 2026-10-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5b0e3c9d7a21'
down_revision: Union[str, Sequence[str], None] = 'f991ffaa5134'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('alerts', 'value')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'alerts',
        sa.Column('value', sa.Numeric(precision=10, scale=3), server_default='0', nullable=False),
    )
