import asyncio
import logging

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from api.device.websocket import send_level_changes
from shared.alert.schemes import LevelChangeMessageScheme
from shared.base.kafka import read_message
from shared.config.settings import config

logger = logging.getLogger(__name__)

RECONNECT_SECONDS = 5


def create_consumer() -> AIOKafkaConsumer:
    """Create consumer that reads every message of the device levels topic from its end without a consumer group."""
    return AIOKafkaConsumer(
        config.kafka.KAFKA_TOPIC_DEVICE_LEVELS,
        bootstrap_servers=config.kafka.KAFKA_HOST,
        group_id=None,
        auto_offset_reset='latest',
    )


async def consume_level_changes() -> None:
    """Read the level changes of the devices from the topic in batches and send them to the websockets."""
    while True:
        consumer = create_consumer()
        try:
            await consumer.start()
            while True:
                result = await consumer.getmany(timeout_ms=1000, max_records=100)
                changes: list[LevelChangeMessageScheme] = []
                for records in result.values():
                    for record in records:
                        change = read_message(record, LevelChangeMessageScheme)
                        if change is not None:
                            changes.append(change)
                if changes:
                    await send_level_changes(changes)
        except KafkaError:
            logger.warning('Device levels are not read: Kafka is unavailable', exc_info=True)
        finally:
            await consumer.stop()
        await asyncio.sleep(RECONNECT_SECONDS)
