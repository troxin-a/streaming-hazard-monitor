from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared import DeviceDB
from shared.device.enums import DeviceType
from shared.device.services import hash_api_key

DEVICE_DATA = {
    'name': 'Датчик CO у печи',
    'serial_number': 'SN-0001',
    'type': DeviceType.CO,
}

NEW_DEVICE = {
    'name': 'Датчик метана',
    'serial_number': 'SN-0100',
    'type': DeviceType.METHANE.value,
}

DEVICE_COUNT = 11

API_KEY = 'test-device-api-key'


async def create_device(
        override_get_async_session: AsyncSession,
        building_uuid: UUID,
        name: str = DEVICE_DATA['name'],
        serial_number: str = DEVICE_DATA['serial_number'],
        device_type: DeviceType = DEVICE_DATA['type'],
        key_hash: str | None = None,
) -> DeviceDB:
    """Create device."""
    device = DeviceDB(
        building_uuid=building_uuid,
        name=name,
        serial_number=serial_number,
        type=device_type,
        key_hash=key_hash,
    )
    override_get_async_session.add(device)
    await override_get_async_session.commit()
    return device


async def create_devices(
        override_get_async_session: AsyncSession,
        building_uuid: UUID,
        count: int = 0,
) -> list[DeviceDB]:
    """Create devices."""
    device_list = [
        DeviceDB(
            building_uuid=building_uuid,
            name=f'{DEVICE_DATA["name"]}{number}',
            serial_number=f'SN-1{number:03d}',
            type=DEVICE_DATA['type'],
        )
        for number in range(count)
    ]
    override_get_async_session.add_all(device_list)
    await override_get_async_session.commit()
    return device_list


@pytest.fixture(scope='function')
async def device(override_get_async_session, building) -> DeviceDB:
    """Device of the building fixture."""
    return await create_device(override_get_async_session, building.uuid)


@pytest.fixture(scope='function')
async def many_devices(override_get_async_session, device, building) -> list[DeviceDB]:
    """Devices that bring the total of the building fixture with the device fixture to DEVICE_COUNT."""
    return await create_devices(override_get_async_session, building.uuid, DEVICE_COUNT - 1)


@pytest.fixture(scope='function')
async def device_with_api_key(override_get_async_session, building) -> DeviceDB:
    """Device of the building fixture with the issued api key API_KEY."""
    return await create_device(
        override_get_async_session,
        building.uuid,
        name='Датчик CO у входа',
        serial_number='SN-0004',
        key_hash=hash_api_key(API_KEY),
    )


@pytest.fixture(scope='function')
async def neighbour_device(override_get_async_session, second_building) -> DeviceDB:
    """Device of another building of the same company."""
    return await create_device(
        override_get_async_session,
        second_building.uuid,
        name='Датчик дыма в офисе',
        serial_number='SN-0002',
        device_type=DeviceType.SMOKE,
    )


@pytest.fixture(scope='function')
async def foreign_device(override_get_async_session, other_building) -> DeviceDB:
    """Device of another company."""
    return await create_device(
        override_get_async_session,
        other_building.uuid,
        name='Датчик метана на складе',
        serial_number='SN-0003',
    )
