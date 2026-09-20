import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, func, UUID, MetaData
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

FK = ForeignKey
mc = mapped_column

NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}


class BaseDBModel(DeclarativeBase):
    """Base PostgresQL database model."""
    __abstract__ = True
    __allow_unmapped__ = True

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    uuid: Mapped[UUID] = mc(UUID(), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mc(server_default=func.now())
    updated_at: Mapped[datetime] = mc(server_default=func.now(), onupdate=func.now())
