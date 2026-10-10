from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared import DefaultThresholdDB, DeviceThresholdDB
from shared.device.enums import AlertLevel, DeviceType

DEFAULT_VALUES = {
    AlertLevel.LEVEL_1: Decimal('20'),
    AlertLevel.LEVEL_2: Decimal('50'),
    AlertLevel.LEVEL_3: Decimal('100'),
    AlertLevel.LEVEL_4: Decimal('300'),
}

DEVICE_VALUES = {
    AlertLevel.LEVEL_1: Decimal('25'),
    AlertLevel.LEVEL_2: Decimal('60'),
    AlertLevel.LEVEL_3: Decimal('120'),
    AlertLevel.LEVEL_4: Decimal('350'),
}

NEW_THRESHOLDS = {
    'level_1': '10.5',
    'level_2': '30',
    'level_3': '75.125',
    'level_4': '200',
}

LEVELS = [level.value for level in AlertLevel]


async def create_default_thresholds(
        override_get_async_session: AsyncSession,
        device_type: DeviceType = DeviceType.CO,
) -> list[DefaultThresholdDB]:
    """Create default thresholds of every level for the device type."""
    threshold_list = [
        DefaultThresholdDB(device_type=device_type, level=level, value=value)
        for level, value in DEFAULT_VALUES.items()
    ]
    override_get_async_session.add_all(threshold_list)
    await override_get_async_session.commit()
    return threshold_list


async def create_device_thresholds(
        override_get_async_session: AsyncSession,
        device_uuid: UUID,
) -> list[DeviceThresholdDB]:
    """Create thresholds of every level for the device."""
    threshold_list = [
        DeviceThresholdDB(device_uuid=device_uuid, level=level, value=value)
        for level, value in DEVICE_VALUES.items()
    ]
    override_get_async_session.add_all(threshold_list)
    await override_get_async_session.commit()
    return threshold_list


@pytest.fixture(scope='function')
async def default_thresholds(override_get_async_session) -> list[DefaultThresholdDB]:
    """Default thresholds of the type of the device fixture."""
    return await create_default_thresholds(override_get_async_session)


@pytest.fixture(scope='function')
async def methane_default_thresholds(override_get_async_session) -> list[DefaultThresholdDB]:
    """Default thresholds of the methane device type."""
    return await create_default_thresholds(override_get_async_session, DeviceType.METHANE)


@pytest.fixture(scope='function')
async def device_thresholds(override_get_async_session, device) -> list[DeviceThresholdDB]:
    """Thresholds set for the device fixture."""
    return await create_device_thresholds(override_get_async_session, device.uuid)


@pytest.fixture(scope='function')
async def foreign_device_thresholds(override_get_async_session, foreign_device) -> list[DeviceThresholdDB]:
    """Thresholds set for the device of another company."""
    return await create_device_thresholds(override_get_async_session, foreign_device.uuid)
