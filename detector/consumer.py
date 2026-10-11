from aiokafka import AIOKafkaConsumer

from shared.config.settings import config


def create_consumer() -> AIOKafkaConsumer:
    """Create consumer of the threshold detector."""
    return AIOKafkaConsumer(
        config.kafka.KAFKA_TOPIC_SENSOR_READINGS,
        bootstrap_servers=config.kafka.KAFKA_HOST,
        group_id=config.kafka.KAFKA_GROUP_THRESHOLD_DETECTOR,
        enable_auto_commit=False,
        auto_offset_reset='earliest',
    )
