import logging
from uuid import UUID

from aiokafka import ConsumerRecord
from pydantic import ValidationError

from detector.devices_state import DeviceState, LEVEL_RANKS
from detector.sessions import DetectorSession
from shared.config.settings import config
from shared.device.enums import AlertLevel
from shared.reading.schemes import ReadingMessageScheme

logger = logging.getLogger(__name__)


def count_reading(state: DeviceState, level: AlertLevel | None) -> bool:
    """Count the level of the reading into the series of the device and change its level at the end of the series."""
    rank = LEVEL_RANKS[level]
    if rank > LEVEL_RANKS[state.level]:
        state.series_count = state.series_count + 1 if state.series_count > 0 else 1
        if state.series_count < config.detector.DETECTOR_RISE_COUNT:
            return False
    elif rank < LEVEL_RANKS[state.level]:
        state.series_count = state.series_count - 1 if state.series_count < 0 else -1
        if -state.series_count < config.detector.DETECTOR_FALL_COUNT:
            return False
    else:
        state.series_count = 0
        return False

    state.level = level
    state.series_count = 0
    return True


async def handle_readings(
        batch: list[ConsumerRecord],
        states: dict[UUID, DeviceState],
        session: DetectorSession,
) -> None:
    """Change the alert of the device when a series of readings of other levels changes its level."""
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

        state.partition = message.partition
        level = max((level for level, ts in state.thresholds.items() if reading.value > ts), default=None)
        if count_reading(state, level):
            readings.append((reading, state.level))

    if readings:
        await session.change_level(readings)

    for reading, level in readings:
        logger.info('Device %s: value %s, level %s', reading.device_uuid, reading.value, level)
