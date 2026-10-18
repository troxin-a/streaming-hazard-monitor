import asyncio
import logging
from uuid import UUID

from aiokafka.errors import CommitFailedError

from detector.consumer import create_consumer, ConsumerRebalancer
from detector.devices_state import DeviceState
from detector.services import handle_readings, refresh_thresholds
from detector.sessions import DetectorSession
from shared.config.session import async_session_maker
from shared.config.settings import config

logger = logging.getLogger(__name__)


async def main() -> None:
    """Run the threshold detector with the device states loaded when partitions are assigned to it."""
    consumer = create_consumer()

    async with async_session_maker() as session:
        detector_session = DetectorSession(session)
        states: dict[UUID, DeviceState] = {}

        consumer.subscribe(
            topics=[config.kafka.KAFKA_TOPIC_SENSOR_READINGS],
            listener=ConsumerRebalancer(states),
        )
        await consumer.start()
        refresh_task = asyncio.create_task(refresh_thresholds(states, consumer))
        try:
            while True:
                result = await consumer.getmany(timeout_ms=1000, max_records=100)
                for tp, messages in result.items():
                    if messages:
                        await handle_readings(messages, states, detector_session)
                        try:
                            await consumer.commit({tp: messages[-1].offset + 1})
                        except CommitFailedError:
                            logger.warning(f'Offset of partition {tp} is not committed: the group has rebalanced')
        finally:
            refresh_task.cancel()
            await consumer.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
