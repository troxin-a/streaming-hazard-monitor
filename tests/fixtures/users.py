from uuid import UUID

import pytest

from shared import UserDB
from tests.base.base_test import BaseTestCase

USER_DATA = {
    'username': 'username',
    'password': BaseTestCase.hashed_password,
    'name': 'Имя',
}

USER_COUNT = 11


async def create_user(
        override_get_async_session,
        building_uuid: UUID | None = None,
        username: str = USER_DATA['username'],
        is_superuser: bool = False,
) -> UserDB:
    """Create user."""
    user_data = USER_DATA.copy()
    user_data['username'] = username
    user = UserDB(building_uuid=building_uuid, is_superuser=is_superuser, **user_data)
    override_get_async_session.add(user)
    await override_get_async_session.commit()
    return user


async def create_users(override_get_async_session, building_uuid: UUID, count: int = 0) -> list[UserDB]:
    """Create users."""
    user_list = []
    for number in range(count):
        username = f'{USER_DATA['username']}{number}'
        user = await create_user(override_get_async_session, building_uuid, username=username)
        user_list.append(user)
    return user_list


@pytest.fixture(scope='function')
async def user(override_get_async_session, building) -> UserDB:
    """User fixture."""
    user = await create_user(override_get_async_session, building.uuid)
    await create_users(override_get_async_session, building.uuid, USER_COUNT - 1)
    return user


@pytest.fixture(scope='function')
async def superuser(override_get_async_session) -> UserDB:
    """Superuser fixture, belongs to no building."""
    return await create_user(override_get_async_session, username='superuser', is_superuser=True)
