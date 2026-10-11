import logging
from decimal import Decimal
from uuid import UUID

from aiokafka import ConsumerRecord
from pydantic import ValidationError

from detector.sessions import DetectorSession
from shared.device.enums import AlertLevel
from shared.reading.schemes import ReadingMessageScheme

logger = logging.getLogger(__name__)


async def handle_reading(
        batch: list[ConsumerRecord],
        thresholds: dict[UUID, dict[AlertLevel, Decimal]],
        levels: dict[UUID, AlertLevel | None],
        session: DetectorSession,
) -> None:
    """Change the alert of the device when the level of the reading from the message differs from its level."""
    readings = []
    for message in batch:
        try:
            reading = ReadingMessageScheme.model_validate_json(message.value)
        except ValidationError:
            logger.exception('Invalid reading message: %r', message)
            continue

        device_thresholds = thresholds.get(reading.device_uuid)
        if device_thresholds is None:
            logger.warning('No thresholds for device %s', reading.device_uuid)
            continue

        level = max((level for level, threshold in device_thresholds.items() if reading.value > threshold), default=None)
        if level == levels.get(reading.device_uuid):
            continue

        levels[reading.device_uuid] = level
        readings.append((reading, level))

    if readings:
        await session.change_level(readings)

    for reading, level in readings:
        logger.info('Device %s: value %s, level %s', reading.device_uuid, reading.value, level)
