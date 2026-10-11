import asyncio
import logging

from detector.consumer import create_consumer
from detector.services import handle_reading
from detector.sessions import DetectorSession
from shared.config.session import async_session_maker


async def main() -> None:
    """Run the threshold detector with the thresholds loaded at the start."""
    async with async_session_maker() as session:
        thresholds = await DetectorSession(session).get_thresholds()
    consumer = create_consumer()
    await consumer.start()
    try:
        async for message in consumer:
            handle_reading(message.value, thresholds)
            await consumer.commit()
    finally:
        await consumer.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
