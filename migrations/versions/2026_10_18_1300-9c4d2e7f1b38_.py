"""unique alert in progress of a device

Revision ID: 9c4d2e7f1b38
Revises: 5b0e3c9d7a21
Create Date: 2026-10-18 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9c4d2e7f1b38'
down_revision: Union[str, Sequence[str], None] = '5b0e3c9d7a21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        op.f('uq_alerts_device_uuid_in_progress'),
        'alerts',
        ['device_uuid'],
        unique=True,
        postgresql_where=sa.text('ended_at IS NULL'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('uq_alerts_device_uuid_in_progress'), table_name='alerts')
