from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared import ReadingDB

READING_DATA = {
    'value': Decimal('37.5'),
}


async def create_reading(
        override_get_async_session: AsyncSession,
        device_uuid: UUID,
        value: Decimal = READING_DATA['value'],
) -> ReadingDB:
    """Create reading."""
    reading = ReadingDB(device_uuid=device_uuid, value=value)
    override_get_async_session.add(reading)
    await override_get_async_session.commit()
    return reading


@pytest.fixture(scope='function')
async def reading(override_get_async_session, device) -> ReadingDB:
    """Reading of the device fixture."""
    return await create_reading(override_get_async_session, device.uuid)
