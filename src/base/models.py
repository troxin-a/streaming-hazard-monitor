import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, func, UUID, MetaData
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

FK = ForeignKey
mc = mapped_column


class BaseDBModel(DeclarativeBase):
    """Base PostgresQL database model."""
    __abstract__ = True
    __allow_unmapped__ = True

    uuid: Mapped[UUID] = mc(UUID(), primary_key=True, default=uuid.uuid4)
    create_date: Mapped[datetime] = mc(server_default=func.now())
    update_date: Mapped[datetime] = mc(server_default=func.now(), onupdate=func.now())


metadata = MetaData()
