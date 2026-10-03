from decimal import Decimal

from sqlalchemy import Numeric, UUID
from sqlalchemy.orm import Mapped

from shared.base.models import BaseDBModel, FK, mc


class ReadingDB(BaseDBModel):
    """Sensor reading database model."""
    __tablename__ = 'readings'

    device_uuid: Mapped[UUID] = mc(UUID(), FK('devices.uuid', ondelete='CASCADE'), index=True)
    value: Mapped[Decimal] = mc(Numeric(10, 3))
