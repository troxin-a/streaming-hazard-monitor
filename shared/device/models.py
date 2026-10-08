from typing import TYPE_CHECKING

from sqlalchemy import Enum, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.base.models import BaseDBModel, FK, mc
from shared.base.utils import enum_values
from shared.device.enums import DeviceType

if TYPE_CHECKING:
    from shared.building.models import BuildingDB


class DeviceDB(BaseDBModel):
    """Device database model."""
    __tablename__ = 'devices'

    name: Mapped[str] = mc(index=True)
    serial_number: Mapped[str] = mc(index=True, unique=True)
    type: Mapped[DeviceType] = mc(Enum(DeviceType, name='device_type', values_callable=enum_values))
    building_uuid: Mapped[UUID] = mc(UUID(), FK('buildings.uuid', ondelete='CASCADE'), index=True)
    key_hash: Mapped[str | None] = mc(index=True, unique=True, nullable=True)

    building: Mapped['BuildingDB'] = relationship(back_populates='devices', lazy='selectin')

    @property
    def has_api_key(self) -> bool:
        """Сообщает, выпущен ли у устройства действующий api-ключ."""
        return self.key_hash is not None
