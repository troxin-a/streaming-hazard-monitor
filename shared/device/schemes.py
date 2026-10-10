from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import Field, model_validator

from shared.base.schemes import BaseScheme
from shared.building.schemes import BuildingScheme
from shared.device.enums import AlertLevel, DeviceType


class DeviceScheme(BaseScheme):
    """Device scheme."""
    uuid: UUID
    name: str
    serial_number: str
    type: DeviceType
    has_api_key: bool
    building: BuildingScheme


class DeviceAPIKeyScheme(BaseScheme):
    """Device api key scheme."""
    key: str


class DeviceCreateScheme(BaseScheme):
    """Device create scheme."""
    name: str
    serial_number: str
    type: DeviceType
    building_uuid: UUID


class DeviceUpdateScheme(BaseScheme):
    """Device update scheme."""
    name: str | None = None
    serial_number: str | None = None
    type: DeviceType | None = None
    building_uuid: UUID | None = None


class ThresholdScheme(BaseScheme):
    """Threshold of a device scheme."""
    level: AlertLevel
    value: Decimal
    is_default: bool


class ThresholdsSetScheme(BaseScheme):
    """Thresholds of every level set for a device scheme."""
    level_1: Decimal = Field(max_digits=10, decimal_places=3)
    level_2: Decimal = Field(max_digits=10, decimal_places=3)
    level_3: Decimal = Field(max_digits=10, decimal_places=3)
    level_4: Decimal = Field(max_digits=10, decimal_places=3)

    @model_validator(mode='after')
    def check_order(self) -> Self:
        """Check that the value of every level is above the value of the previous one."""
        if not self.level_1 < self.level_2 < self.level_3 < self.level_4:
            raise ValueError('The threshold of every level must be above the threshold of the previous level')
        return self

    def by_level(self) -> dict[AlertLevel, Decimal]:
        """Return threshold values by their levels in the ascending order of the levels."""
        return {level: getattr(self, level.value) for level in AlertLevel}
