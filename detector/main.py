import asyncio
import logging

from detector.consumer import create_consumer
from detector.services import handle_reading
from detector.sessions import DetectorSession
from shared.config.session import async_session_maker


async def main() -> None:
    """Run the threshold detector with the thresholds and the alert levels loaded at the start."""
    consumer = create_consumer()
    async with async_session_maker() as session:
        detector_session = DetectorSession(session)
        thresholds = await detector_session.get_thresholds()
        levels = await detector_session.get_levels()

        await consumer.start()
        try:
            while True:
                result = await consumer.getmany(timeout_ms=1000, max_records=100)
                for tp, messages in result.items():
                    if messages:
                        await handle_reading(messages, thresholds, levels, detector_session)
                        await consumer.commit({tp: messages[-1].offset + 1})
        finally:
            await consumer.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
