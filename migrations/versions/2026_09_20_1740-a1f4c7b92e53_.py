"""empty message

Revision ID: a1f4c7b92e53
Revises: d786836f6b40
Create Date: 2026-09-20 17:40:12.114302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1f4c7b92e53'
down_revision: Union[str, Sequence[str], None] = 'd786836f6b40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role = sa.Enum('employee', 'director', name='user_role')


def upgrade() -> None:
    """Upgrade schema."""
    user_role.create(op.get_bind())
    op.add_column('users', sa.Column('role', user_role, server_default='employee', nullable=False))
    op.add_column('users', sa.Column('company_uuid', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_users_company_uuid'), 'users', ['company_uuid'], unique=False)
    op.create_foreign_key(op.f('fk_users_company_uuid_companies'), 'users', 'companies', ['company_uuid'], ['uuid'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_users_company_uuid_companies'), 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_company_uuid'), table_name='users')
    op.drop_column('users', 'company_uuid')
    op.drop_column('users', 'role')
    user_role.drop(op.get_bind())
