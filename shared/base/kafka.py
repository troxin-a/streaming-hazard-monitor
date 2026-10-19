import logging

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRebalanceListener, ConsumerRecord, TopicPartition
from pydantic import BaseModel, ValidationError

from shared.config.settings import config

logger = logging.getLogger(__name__)


def create_consumer(
        topics: list[str] | None = None,
        group_id: str | None = None,
        auto_offset_reset: str = 'latest',
        listener: ConsumerRebalanceListener | None = None,
) -> AIOKafkaConsumer:
    """Create consumer that commits offsets only manually, subscribed to the topics with the listener when given."""
    consumer = AIOKafkaConsumer(
        bootstrap_servers=config.kafka.KAFKA_HOST,
        group_id=group_id,
        enable_auto_commit=False,
        auto_offset_reset=auto_offset_reset,
    )
    if topics:
        consumer.subscribe(topics, listener=listener)
    return consumer


def create_producer(request_timeout_ms: int = 40000) -> AIOKafkaProducer:
    """Create producer that waits for the broker no longer than the timeout."""
    return AIOKafkaProducer(bootstrap_servers=config.kafka.KAFKA_HOST, request_timeout_ms=request_timeout_ms)


def read_message[Scheme: BaseModel](record: ConsumerRecord[bytes, bytes], scheme: type[Scheme]) -> Scheme | None:
    """Read the message by the scheme or return none when it has no value or does not match the scheme."""
    value = record.value
    if value is None:
        logger.warning(f'Message without a value: {record}')
        return None
    try:
        return scheme.model_validate_json(value)
    except ValidationError as error:
        logger.warning(f'Message does not match {scheme.__name__}: {record}, {error}')
        return None


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
