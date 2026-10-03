from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared import BuildingDB

BUILDING_DATA = {
    'name': 'Цех №1',
}

NEW_BUILDING = {
    'name': 'Офис',
}

BUILDING_COUNT = 11


async def create_building(
        override_get_async_session: AsyncSession,
        company_uuid: UUID,
        name: str = BUILDING_DATA['name'],
) -> BuildingDB:
    """Create building."""
    building = BuildingDB(company_uuid=company_uuid, name=name)
    override_get_async_session.add(building)
    await override_get_async_session.commit()
    return building


async def create_buildings(
        override_get_async_session: AsyncSession,
        company_uuid: UUID,
        count: int = 0,
) -> list[BuildingDB]:
    """Create buildings."""
    building_list = [
        BuildingDB(company_uuid=company_uuid, name=f'{BUILDING_DATA["name"]}{number}') for number in range(count)
    ]
    override_get_async_session.add_all(building_list)
    await override_get_async_session.commit()
    return building_list


@pytest.fixture(scope='function')
async def building(override_get_async_session, company) -> BuildingDB:
    """Building of the company fixture."""
    return await create_building(override_get_async_session, company.uuid)


@pytest.fixture(scope='function')
async def many_buildings(override_get_async_session, building, company) -> list[BuildingDB]:
    """Buildings that bring the total of the company fixture with the building fixture to BUILDING_COUNT."""
    return await create_buildings(override_get_async_session, company.uuid, BUILDING_COUNT - 1)


@pytest.fixture(scope='function')
async def second_building(override_get_async_session, company) -> BuildingDB:
    """Another building of the company fixture."""
    return await create_building(override_get_async_session, company.uuid, name='Офис')


@pytest.fixture(scope='function')
async def other_building(override_get_async_session, other_company) -> BuildingDB:
    """Building of another company."""
    return await create_building(override_get_async_session, other_company.uuid, name='Склад')
