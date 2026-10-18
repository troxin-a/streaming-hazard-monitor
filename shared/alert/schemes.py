from datetime import datetime
from uuid import UUID

from shared.base.schemes import BaseScheme
from shared.device.enums import AlertLevel, DeviceType


class AlertDeviceScheme(BaseScheme):
    """Device of an alert scheme."""
    uuid: UUID
    name: str
    type: DeviceType


class AlertBuildingScheme(BaseScheme):
    """Building of an alert scheme."""
    uuid: UUID
    name: str


class AlertScheme(BaseScheme):
    """Alert scheme."""
    uuid: UUID
    level: AlertLevel
    started_at: datetime
    device: AlertDeviceScheme
    building: AlertBuildingScheme
