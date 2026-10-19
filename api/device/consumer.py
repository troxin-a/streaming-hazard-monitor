import asyncio
import logging

from aiokafka.errors import KafkaError

from api.device.services import broadcast_level_changes, broadcast_readings
from api.device.websocket import device_websockets
from shared.alert.schemes import LevelChangeMessageScheme
from shared.base.kafka import create_consumer, read_batch
from shared.config.settings import config
from shared.reading.schemes import ReadingMessageScheme

logger = logging.getLogger(__name__)

RECONNECT_SECONDS = 5
READINGS_SEND_SECONDS = 1


async def consume_level_changes_to_websockets() -> None:
    """Read the level changes of the devices from the topic in batches and send them to the websockets."""
    while True:
        consumer = create_consumer([config.kafka.KAFKA_TOPIC_DEVICE_LEVELS])
        try:
            await consumer.start()
            while True:
                batch = await consumer.getmany(timeout_ms=1000, max_records=100)
                changes = read_batch(batch, LevelChangeMessageScheme)
                if changes:
                    await broadcast_level_changes(changes)
        except KafkaError as error:
            logger.warning(f'Device levels are not read: Kafka is unavailable: {error}')
        finally:
            await consumer.stop()
        await asyncio.sleep(RECONNECT_SECONDS)


async def consume_readings_to_websockets() -> None:
    """Take the readings of the devices fetched from the topic every second and send them to the websockets."""
    while True:
        consumer = create_consumer([config.kafka.KAFKA_TOPIC_SENSOR_READINGS])
        try:
            await consumer.start()
            while True:
                await asyncio.sleep(READINGS_SEND_SECONDS)
                batch = await consumer.getmany()
                if device_websockets.has_subscriptions():
                    readings = read_batch(batch, ReadingMessageScheme)
                    if readings:
                        await broadcast_readings(readings)
        except KafkaError as error:
            logger.warning(f'Device readings are not read: Kafka is unavailable: {error}')
        finally:
            await consumer.stop()
        await asyncio.sleep(RECONNECT_SECONDS)
