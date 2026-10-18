from datetime import datetime

from sqlalchemy import DateTime, Enum, UUID
from sqlalchemy.orm import Mapped

from shared.base.models import BaseDBModel, FK, mc
from shared.base.utils import enum_values
from shared.device.enums import AlertLevel


class AlertDB(BaseDBModel):
    """Alert database model."""
    __tablename__ = 'alerts'

    device_uuid: Mapped[UUID] = mc(UUID(), FK('devices.uuid', ondelete='CASCADE'), index=True)
    building_uuid: Mapped[UUID] = mc(UUID(), FK('buildings.uuid', ondelete='CASCADE'), index=True)
    level: Mapped[AlertLevel] = mc(Enum(AlertLevel, name='alert_level', values_callable=enum_values))
    started_at: Mapped[datetime] = mc(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mc(DateTime(timezone=True), nullable=True)
