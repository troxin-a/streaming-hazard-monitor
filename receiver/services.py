import asyncio
import logging
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from receiver.sessions import TelemetrySession
from shared.config.session import async_session_maker
from shared.config.settings import config

logger = logging.getLogger(__name__)


async def reload_devices(session: AsyncSession, devices: dict[str, UUID]) -> None:
    """Replace the content of the devices dictionary with the devices loaded from the database."""
    loaded = await TelemetrySession(session).get_devices()
    devices.clear()
    devices.update(loaded)


async def refresh_devices(devices: dict[str, UUID]) -> None:
    """Reload the devices dictionary from the database at the configured interval."""
    while True:
        await asyncio.sleep(config.receiver.RECEIVER_DEVICES_REFRESH_SECONDS)
        try:
            async with async_session_maker() as session:
                await reload_devices(session, devices)
        except (SQLAlchemyError, OSError) as error:
            logger.warning(f'Devices are not reloaded: the database is unavailable: {error}')
