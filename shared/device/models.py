from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Numeric, UniqueConstraint, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.base.models import BaseDBModel, FK, mc
from shared.base.utils import enum_values
from shared.device.enums import AlertLevel, DeviceType

if TYPE_CHECKING:
    from shared.building.models import BuildingDB


class DeviceDB(BaseDBModel):
    """Device database model."""
    __tablename__ = 'devices'

    name: Mapped[str] = mc(index=True)
    serial_number: Mapped[str] = mc(index=True, unique=True)
    type: Mapped[DeviceType] = mc(Enum(DeviceType, name='device_type', values_callable=enum_values))
    building_uuid: Mapped[UUID] = mc(UUID(), FK('buildings.uuid'), index=True)
    key_hash: Mapped[str | None] = mc(index=True, unique=True, nullable=True)

    building: Mapped['BuildingDB'] = relationship(back_populates='devices', lazy='selectin')

    @property
    def has_api_key(self) -> bool:
        """Сообщает, выпущен ли у устройства действующий api-ключ."""
        return self.key_hash is not None


class ThresholdValueMixin:
    """Alert level with the value the readings above which raise it."""
    level: Mapped[AlertLevel] = mc(Enum(AlertLevel, name='alert_level', values_callable=enum_values))
    value: Mapped[Decimal] = mc(Numeric(10, 3))


class DefaultThresholdDB(ThresholdValueMixin, BaseDBModel):
    """Default threshold of a device type database model."""
    __tablename__ = 'default_thresholds'
    __table_args__ = (UniqueConstraint('device_type', 'level'),)

    device_type: Mapped[DeviceType] = mc(Enum(DeviceType, name='device_type', values_callable=enum_values))


class DeviceThresholdDB(ThresholdValueMixin, BaseDBModel):
    """Threshold set for a device database model."""
    __tablename__ = 'device_thresholds'
    __table_args__ = (UniqueConstraint('device_uuid', 'level'),)

    device_uuid: Mapped[UUID] = mc(UUID(), FK('devices.uuid', ondelete='CASCADE'))

    @property
    def is_default(self) -> bool:
        return False
