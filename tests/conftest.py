import random
import uuid
from typing import AsyncGenerator, Literal

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.main import app
from shared.base.models import BaseDBModel
from shared.config.session import get_async_session
from shared.config.settings import config

pytest_plugins = [
    'tests.fixtures.building',
    'tests.fixtures.users',
]

test_db = f'test_{uuid.uuid4()}'.replace('-', '')


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
    root_db_url = config.database.root_database_url
    config.database.database_url = root_db_url

    engine = create_async_engine(root_db_url, isolation_level='AUTOCOMMIT')
    async with engine.connect() as conn:
        try:
            await conn.execute(text(f'CREATE DATABASE {test_db}'))
            yield
        finally:
            await conn.execute(text(f'DROP DATABASE IF EXISTS {test_db} with (force)'))


db_url = config.database.get_test_db_url(test_db)
config.database.database_url = db_url
engine_test = create_async_engine(db_url)

async_session_maker = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Override async session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


if not hasattr(app, 'dependency_overrides'):
    app.dependency_overrides = {}
app.dependency_overrides[get_async_session] = override_async_session


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
    async with engine_test.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.drop_all)
        await conn.run_sync(BaseDBModel.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.drop_all)
