"""empty message

Revision ID: c3e9a5d17b48
Revises: 8af6173104c0
Create Date: 2026-10-03 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3e9a5d17b48'
down_revision: Union[str, Sequence[str], None] = '8af6173104c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('readings',
    sa.Column('device_uuid', sa.UUID(), nullable=False),
    sa.Column('value', sa.Numeric(precision=10, scale=3), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['device_uuid'], ['devices.uuid'], name=op.f('fk_readings_device_uuid_devices')),
    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_readings'))
    )
    op.create_index(op.f('ix_readings_device_uuid'), 'readings', ['device_uuid'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_readings_device_uuid'), table_name='readings')
    op.drop_table('readings')
