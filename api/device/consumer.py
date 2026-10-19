import asyncio
import logging

from aiokafka import AIOKafkaConsumer, ConsumerRecord, TopicPartition
from aiokafka.errors import KafkaError
from pydantic import BaseModel

from api.device.services import send_level_changes, send_readings
from api.device.websocket import device_websockets
from shared.alert.schemes import LevelChangeMessageScheme
from shared.base.kafka import read_message
from shared.config.settings import config
from shared.reading.schemes import ReadingMessageScheme

logger = logging.getLogger(__name__)

RECONNECT_SECONDS = 5
READINGS_SEND_SECONDS = 1


def create_consumer(topic: str) -> AIOKafkaConsumer:
    """Create consumer that reads every message of the topic from its end without a consumer group."""
    return AIOKafkaConsumer(
        topic,
        bootstrap_servers=config.kafka.KAFKA_HOST,
        group_id=None,
        auto_offset_reset='latest',
    )


def read_batch[Scheme: BaseModel](
        batch: dict[TopicPartition, list[ConsumerRecord[bytes, bytes]]],
        scheme: type[Scheme],
) -> list[Scheme]:
    """Read the messages of the batch by the scheme, skipping the ones that do not match it."""
    messages: list[Scheme] = []
    for records in batch.values():
        for record in records:
            message = read_message(record, scheme)
            if message is not None:
                messages.append(message)
    return messages


async def consume_level_changes() -> None:
    """Read the level changes of the devices from the topic in batches and send them to the websockets."""
    while True:
        consumer = create_consumer(config.kafka.KAFKA_TOPIC_DEVICE_LEVELS)
        try:
            await consumer.start()
            while True:
                batch = await consumer.getmany(timeout_ms=1000, max_records=100)
                changes = read_batch(batch, LevelChangeMessageScheme)
                if changes:
                    await send_level_changes(changes)
        except KafkaError as error:
            logger.warning(f'Device levels are not read: Kafka is unavailable: {error}')
        finally:
            await consumer.stop()
        await asyncio.sleep(RECONNECT_SECONDS)


async def consume_readings() -> None:
    """Take the readings of the devices fetched from the topic every second and send them to the websockets."""
    while True:
        consumer = create_consumer(config.kafka.KAFKA_TOPIC_SENSOR_READINGS)
        try:
            await consumer.start()
            while True:
                await asyncio.sleep(READINGS_SEND_SECONDS)
                batch = await consumer.getmany()
                if device_websockets.devices:
                    readings = read_batch(batch, ReadingMessageScheme)
                    if readings:
                        await send_readings(readings)
        except KafkaError as error:
            logger.warning(f'Device readings are not read: Kafka is unavailable: {error}')
        finally:
            await consumer.stop()
        await asyncio.sleep(RECONNECT_SECONDS)
