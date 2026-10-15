from dataclasses import dataclass
from decimal import Decimal

from shared.device.enums import AlertLevel


@dataclass(slots=True)
class DeviceState:
    """State of the device kept by the threshold detector."""
    thresholds: dict[AlertLevel, Decimal]
    level: AlertLevel | None = None
