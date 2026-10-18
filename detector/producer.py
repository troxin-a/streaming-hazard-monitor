from aiokafka import AIOKafkaProducer

from shared.alert.schemes import LevelChangeMessageScheme
from shared.config.settings import config
from shared.device.enums import AlertLevel
from shared.reading.schemes import ReadingMessageScheme


def create_producer() -> AIOKafkaProducer:
    """Create producer of the threshold detector."""
    return AIOKafkaProducer(bootstrap_servers=config.kafka.KAFKA_HOST)


async def send_level_changes(
        producer: AIOKafkaProducer,
        changes: list[tuple[ReadingMessageScheme, AlertLevel | None]],
) -> None:
    """Send the level changes of the devices to the device levels topic in their order."""
    topic = config.kafka.KAFKA_TOPIC_DEVICE_LEVELS
    for reading, level in changes:
        change = LevelChangeMessageScheme(device_uuid=reading.device_uuid, level=level, changed_at=reading.received_at)
        message = change.model_dump_json().encode()
        key = str(change.device_uuid).encode()
        await producer.send_and_wait(topic, message, key)
