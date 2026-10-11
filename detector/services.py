import logging
from decimal import Decimal
from uuid import UUID

from pydantic import ValidationError

from shared.device.enums import AlertLevel
from shared.reading.schemes import ReadingMessageScheme

logger = logging.getLogger(__name__)


def detect_level(value: Decimal, thresholds: dict[AlertLevel, Decimal]) -> AlertLevel | None:
    """Return the highest alert level the value is above the threshold of."""
    return max((level for level, threshold in thresholds.items() if value > threshold), default=None)


def handle_reading(message: bytes, thresholds: dict[UUID, dict[AlertLevel, Decimal]]) -> AlertLevel | None:
    """Return the alert level of the reading from the message of the readings topic."""
    try:
        reading = ReadingMessageScheme.model_validate_json(message)
    except ValidationError:
        logger.exception('Invalid reading message: %r', message)
        return None

    device_thresholds = thresholds.get(reading.device_uuid)
    if device_thresholds is None:
        logger.warning('No thresholds for device %s', reading.device_uuid)
        return None

    level = detect_level(reading.value, device_thresholds)
    if level is not None:
        logger.info('Device %s: value %s is %s', reading.device_uuid, reading.value, level.value)
    return level
