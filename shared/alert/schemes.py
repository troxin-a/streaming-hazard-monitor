from datetime import datetime
from uuid import UUID

from shared.base.schemes import BaseScheme
from shared.device.enums import AlertLevel


class LevelChangeMessageScheme(BaseScheme):
    """Level change of a device message scheme."""
    device_uuid: UUID
    level: AlertLevel | None
    changed_at: datetime
