import logging
from decimal import Decimal
from uuid import UUID

from pydantic import ValidationError

from detector.sessions import DetectorSession
from shared.device.enums import AlertLevel
from shared.reading.schemes import ReadingMessageScheme

logger = logging.getLogger(__name__)


async def handle_reading(
        message: bytes,
        thresholds: dict[UUID, dict[AlertLevel, Decimal]],
        levels: dict[UUID, AlertLevel],
        session: DetectorSession,
) -> None:
    """Change the alert of the device when the level of the reading from the message differs from its level."""
    try:
        reading = ReadingMessageScheme.model_validate_json(message)
    except ValidationError:
        logger.exception('Invalid reading message: %r', message)
        return

    device_thresholds = thresholds.get(reading.device_uuid)
    if device_thresholds is None:
        logger.warning('No thresholds for device %s', reading.device_uuid)
        return

    level = max((level for level, threshold in device_thresholds.items() if reading.value > threshold), default=None)
    if level == levels.get(reading.device_uuid):
        return

    await session.change_level(reading, level)
    if level is None:
        del levels[reading.device_uuid]
    else:
        levels[reading.device_uuid] = level
    logger.info('Device %s: value %s, level %s', reading.device_uuid, reading.value, level)
