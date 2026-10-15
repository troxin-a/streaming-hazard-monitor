import logging
from uuid import UUID

from aiokafka import ConsumerRecord
from pydantic import ValidationError

from detector.devices_state import DeviceState
from detector.sessions import DetectorSession
from shared.reading.schemes import ReadingMessageScheme

logger = logging.getLogger(__name__)


async def handle_readings(
        batch: list[ConsumerRecord],
        states: dict[UUID, DeviceState],
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

        state = states.get(reading.device_uuid)
        if state is None:
            logger.warning('No thresholds for device %s', reading.device_uuid)
            continue

        level = max((level for level, ts in state.thresholds.items() if reading.value > ts), default=None)
        if level == state.level:
            continue

        state.level = level
        readings.append((reading, level))

    if readings:
        await session.change_level(readings)

    for reading, level in readings:
        logger.info('Device %s: value %s, level %s', reading.device_uuid, reading.value, level)
