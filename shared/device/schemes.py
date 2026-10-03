from uuid import UUID

from shared.base.schemes import BaseScheme
from shared.building.schemes import BuildingScheme
from shared.device.enums import DeviceType


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
