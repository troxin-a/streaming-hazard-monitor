"""empty message

Revision ID: e7b2d4f09a61
Revises: c3e9a5d17b48
Create Date: 2026-10-03 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e7b2d4f09a61'
down_revision: Union[str, Sequence[str], None] = 'c3e9a5d17b48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f('fk_readings_device_uuid_devices'), 'readings', type_='foreignkey')
    op.create_foreign_key(
        op.f('fk_readings_device_uuid_devices'), 'readings', 'devices', ['device_uuid'], ['uuid'], ondelete='CASCADE',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_readings_device_uuid_devices'), 'readings', type_='foreignkey')
    op.create_foreign_key(op.f('fk_readings_device_uuid_devices'), 'readings', 'devices', ['device_uuid'], ['uuid'])
