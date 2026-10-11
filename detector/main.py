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
            async for message in consumer:
                await handle_reading(message.value, thresholds, levels, detector_session)
                await consumer.commit()
        finally:
            await consumer.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
