import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared import CompanyDB

COMPANY_DATA = {
    'name': 'ООО Металлстрой',
}

NEW_COMPANY = {
    'name': 'ЗАО Химпром',
}

COMPANY_COUNT = 11


async def create_company(override_get_async_session: AsyncSession, name: str = COMPANY_DATA['name']) -> CompanyDB:
    """Create company."""
    company = CompanyDB(name=name)
    override_get_async_session.add(company)
    await override_get_async_session.commit()
    return company


async def create_companies(override_get_async_session: AsyncSession, count: int = 0) -> list[CompanyDB]:
    """Create companies."""
    company_list = [CompanyDB(name=f'{COMPANY_DATA["name"]}{number}') for number in range(count)]
    override_get_async_session.add_all(company_list)
    await override_get_async_session.commit()
    return company_list


@pytest.fixture(scope='function')
async def company(override_get_async_session) -> CompanyDB:
    """Company fixture."""
    return await create_company(override_get_async_session)


@pytest.fixture(scope='function')
async def many_companies(override_get_async_session, company) -> list[CompanyDB]:
    """Companies that bring the total with the company fixture to COMPANY_COUNT."""
    return await create_companies(override_get_async_session, COMPANY_COUNT - 1)


@pytest.fixture(scope='function')
async def other_company(override_get_async_session) -> CompanyDB:
    """Another company."""
    return await create_company(override_get_async_session, name='ООО Северсклад')
