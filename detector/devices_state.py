from dataclasses import dataclass
from decimal import Decimal

from shared.device.enums import AlertLevel

LEVEL_RANKS: dict[AlertLevel | None, int] = {
    None: 0,
    AlertLevel.LEVEL_1: 1,
    AlertLevel.LEVEL_2: 2,
    AlertLevel.LEVEL_3: 3,
    AlertLevel.LEVEL_4: 4,
}


@dataclass(slots=True)
class DeviceState:
    """State of the device kept by the threshold detector."""
    thresholds: dict[AlertLevel, Decimal]
    level: AlertLevel | None = None
    series_count: int = 0
