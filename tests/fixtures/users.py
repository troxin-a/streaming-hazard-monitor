import pytest

from shared import UserDB
from tests.base.base_test import BaseTestCase

USER_DATA = {
    'username': 'username',
    'password': BaseTestCase.hashed_password,
    'name': 'Имя',
}

USER_COUNT = 11


async def create_users(override_get_async_session, count: int = 0):
    """Create users."""
    user_data = USER_DATA.copy()
    user_list = []
    for _ in range(count):
        user_data['username'] = f'{user_data['username']}{_}'
        user = UserDB(**user_data)
        override_get_async_session.add(user)
        await override_get_async_session.commit()
        user_list.append(user)


async def create_user(override_get_async_session):
    """Create user."""
    user_data = USER_DATA.copy()
    user = UserDB(**user_data)
    override_get_async_session.add(user)
    await override_get_async_session.commit()
    return user


@pytest.fixture(scope='function')
async def user(override_get_async_session):
    """User fixture."""
    user = await create_user(override_get_async_session)
    await create_users(override_get_async_session, USER_COUNT - 1)
    return user
