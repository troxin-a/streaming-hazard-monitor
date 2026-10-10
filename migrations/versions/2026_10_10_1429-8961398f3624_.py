"""Default thresholds of every device type

Revision ID: 8961398f3624
Revises: 1584e527bc3a
Create Date: 2026-10-10 14:29:28.698118

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8961398f3624'
down_revision: Union[str, Sequence[str], None] = '1584e527bc3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Примерные значения для учебного проекта, по уровням 1-4.
DEFAULT_THRESHOLDS = {
    'co': (20, 50, 100, 300),               # ppm
    'co2': (1000, 2000, 5000, 15000),       # ppm
    'methane': (5, 10, 20, 50),             # % НКПР
    'smoke': (0.05, 0.1, 0.15, 0.2),        # дБ/м
    'temperature': (54, 64, 69, 84),        # °C
    'radiation': (0.3, 0.6, 1.2, 6),        # мкЗв/ч
}


def upgrade() -> None:
    """Upgrade schema."""
    rows = ', '.join(
        f"(gen_random_uuid(), '{device_type}', 'level_{number}', {value})"
        for device_type, values in DEFAULT_THRESHOLDS.items()
        for number, value in enumerate(values, start=1)
    )
    op.execute(f'INSERT INTO default_thresholds (uuid, device_type, level, value) VALUES {rows}')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DELETE FROM default_thresholds')
