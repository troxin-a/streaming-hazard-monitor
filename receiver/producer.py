from aiokafka import AIOKafkaProducer
from starlette.requests import Request

from shared.config.settings import config
from shared.reading.schemes import ReadingMessageScheme


def create_producer() -> AIOKafkaProducer:
    """Create producer of the telemetry receiver."""
    return AIOKafkaProducer(bootstrap_servers=config.kafka.KAFKA_HOST)


def get_producer(request: Request) -> AIOKafkaProducer:
    """Return producer of the running application."""
    return request.state.telemetry_producer


async def send_reading(producer: AIOKafkaProducer, reading: ReadingMessageScheme) -> None:
    """Send the reading to the readings topic."""
    topic = config.kafka.KAFKA_TOPIC_SENSOR_READINGS
    message = reading.model_dump_json().encode()
    key = str(reading.device_uuid).encode()
    await producer.send_and_wait(topic, message, key)
