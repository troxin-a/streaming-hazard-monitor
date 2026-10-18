import random
import uuid
from typing import AsyncGenerator, Literal

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from shared.config.settings import config

test_db = f'test_{uuid.uuid4()}'.replace('-', '')
# Set before the imports below: the engine of the application is created on import with this url
config.database.database_url = config.database.get_test_db_url(test_db)

from shared.base.models import BaseDBModel  # noqa: E402
from shared.config.session import async_session_maker, engine  # noqa: E402

pytest_plugins = [
    'tests.fixtures.alert',
    'tests.fixtures.building',
    'tests.fixtures.company',
    'tests.fixtures.detector',
    'tests.fixtures.device',
    'tests.fixtures.producer',
    'tests.fixtures.threshold',
    'tests.fixtures.users',
]


def get_random_value(length: int = 10, value_type: Literal['str', 'int', 'float'] = 'str') -> str | int | float:
    """Getting a random value."""
    value = random.randint(0, 10 ** length - 1)
    result = f'{value:0{length}}'
    return result if value_type == 'str' else int(result) if value_type == 'int' else float(result)


def get_url_size(url: str, size: int, page: int = None) -> str:
    """Get url size."""
    url = f'{url}?size={size}'
    if page:
        url += f'&page={page}'
    return url


def get_url_size2(url: str, size: int, page: int = None) -> str:
    """Get url size2."""
    url = f'{url}&size={size}'
    if page:
        url += f'&page={page}'
    return url


@pytest.fixture(scope="session", autouse=True)
async def create_test_database():
    """Create test database."""
    root_engine = create_async_engine(config.database.root_database_url, isolation_level='AUTOCOMMIT')
    async with root_engine.connect() as conn:
        try:
            await conn.execute(text(f'CREATE DATABASE {test_db}'))
            yield
        finally:
            await conn.execute(text(f'DROP DATABASE IF EXISTS {test_db} with (force)'))


@pytest.fixture(scope='function')
async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Override async session fixture."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(autouse=True, scope='function')
async def prepare_database():
    """Prepare database."""
    async with engine.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.drop_all)
        await conn.run_sync(BaseDBModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.drop_all)
