import asyncio
import logging
from uuid import UUID

from detector.consumer import ConsumerRebalancer, consume_readings
from detector.devices_state import DeviceState
from detector.services import refresh_thresholds
from shared.base.kafka import create_consumer, create_producer
from shared.config.session import async_session_maker
from shared.config.settings import config


async def main() -> None:
    """Run the threshold detector with the device states loaded when partitions are assigned to it."""
    states: dict[UUID, DeviceState] = {}
    consumer = create_consumer(
        [config.kafka.KAFKA_TOPIC_SENSOR_READINGS],
        group_id=config.kafka.KAFKA_GROUP_THRESHOLD_DETECTOR,
        auto_offset_reset='earliest',
        listener=ConsumerRebalancer(states),
    )
    producer = create_producer()

    async with async_session_maker() as session:
        await producer.start()
        await consumer.start()
        refresh_task = asyncio.create_task(refresh_thresholds(states, consumer))
        try:
            await consume_readings(consumer, producer, states, session)
        finally:
            refresh_task.cancel()
            await consumer.stop()
            await producer.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
