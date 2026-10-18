import asyncio
import logging
from uuid import UUID

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from detector.devices_state import DeviceState, LEVEL_RANKS
from detector.producer import send_level_changes
from detector.sessions import DetectorSession
from shared.config.session import async_session_maker
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


def handle_readings(
        batch: list[ConsumerRecord],
        states: dict[UUID, DeviceState],
) -> list[tuple[ReadingMessageScheme, AlertLevel | None]]:
    """Count the readings of the batch into the series of their devices and return the level changes."""
    readings: list[tuple[ReadingMessageScheme, AlertLevel | None]] = []
    for message in batch:
        try:
            reading = ReadingMessageScheme.model_validate_json(message.value)
        except ValidationError:
            logger.exception(f'Invalid reading message: {message}')
            continue

        state = states.get(reading.device_uuid)
        if state is None:
            logger.warning(f'No thresholds for device {reading.device_uuid}')
            continue

        state.partition = message.partition
        level = max((level for level, ts in state.thresholds.items() if reading.value > ts), default=None)
        if count_reading(state, level):
            readings.append((reading, state.level))
    return readings


async def save_level_changes(
        changes: list[tuple[ReadingMessageScheme, AlertLevel | None]],
        producer: AIOKafkaProducer,
        session: DetectorSession,
) -> None:
    """Send the level changes to the device levels topic and then save them as alerts."""
    if not changes:
        return
    await send_level_changes(producer, changes)
    await session.change_level(changes)
    for reading, level in changes:
        logger.info(f'Device {reading.device_uuid}: value {reading.value}, level {level}')


async def reload_states(states: dict[UUID, DeviceState], kept: set[int]) -> None:
    """Replace the states with the ones from the database keeping the levels and series of the kept partitions."""
    try:
        async with async_session_maker() as session:
            new_states = await DetectorSession(session).get_states()
    except (SQLAlchemyError, OSError):
        logger.warning('States are not reloaded: the database is unavailable', exc_info=True)
        return
    for device_uuid, new_state in new_states.items():
        old_state = states.get(device_uuid)
        if old_state is not None and old_state.partition in kept:
            new_state.level = old_state.level
            new_state.series_count = old_state.series_count
            new_state.partition = old_state.partition
    states.clear()
    states.update(new_states)


async def refresh_thresholds(states: dict[UUID, DeviceState], consumer: AIOKafkaConsumer) -> None:
    """Reload the thresholds of the devices from the database at the configured interval."""
    while True:
        await asyncio.sleep(config.detector.DETECTOR_THRESHOLDS_REFRESH_SECONDS)
        kept = {tp.partition for tp in consumer.assignment()}
        await reload_states(states, kept)
