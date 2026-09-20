import pytest

from shared import BuildingDB, CompanyDB

COMPANY_DATA = {
    'name': 'ООО Металлстрой',
}

BUILDING_DATA = {
    'name': 'Цех №1',
}


async def create_company(override_get_async_session, name: str = COMPANY_DATA['name']) -> CompanyDB:
    """Create company."""
    company = CompanyDB(name=name)
    override_get_async_session.add(company)
    await override_get_async_session.commit()
    return company


async def create_building(override_get_async_session, name: str = BUILDING_DATA['name']) -> BuildingDB:
    """Create building with its company."""
    company = await create_company(override_get_async_session)
    building = BuildingDB(company_uuid=company.uuid, name=name)
    override_get_async_session.add(building)
    await override_get_async_session.commit()
    return building


@pytest.fixture(scope='function')
async def company(override_get_async_session) -> CompanyDB:
    """Company fixture."""
    return await create_company(override_get_async_session)


@pytest.fixture(scope='function')
async def building(override_get_async_session) -> BuildingDB:
    """Building fixture."""
    return await create_building(override_get_async_session)


@pytest.fixture(scope='function')
async def second_building(override_get_async_session, building) -> BuildingDB:
    """Another building of the same company."""
    second = BuildingDB(company_uuid=building.company_uuid, name='Офис')
    override_get_async_session.add(second)
    await override_get_async_session.commit()
    return second
