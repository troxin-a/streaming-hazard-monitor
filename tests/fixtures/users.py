from uuid import UUID

import pytest

from shared import UserDB
from shared.user.enums import UserRole
from tests.base.base_test import BaseTestCase
from tests.fixtures.building import create_building

USER_DATA = {
    'username': 'username',
    'password': BaseTestCase.hashed_password,
    'name': 'Имя',
}

USER_COUNT = 11


async def create_user(
        override_get_async_session,
        building_uuid: UUID | None = None,
        company_uuid: UUID | None = None,
        username: str = USER_DATA['username'],
        is_superuser: bool = False,
        role: UserRole = UserRole.EMPLOYEE,
) -> UserDB:
    """Create user."""
    user_data = USER_DATA.copy()
    user_data['username'] = username
    user = UserDB(
        building_uuid=building_uuid,
        company_uuid=company_uuid,
        is_superuser=is_superuser,
        role=role,
        **user_data,
    )
    override_get_async_session.add(user)
    await override_get_async_session.commit()
    return user


async def create_users(
        override_get_async_session,
        building_uuid: UUID,
        company_uuid: UUID,
        count: int = 0,
) -> list[UserDB]:
    """Create users."""
    user_list = []
    for number in range(count):
        username = f'{USER_DATA['username']}{number}'
        user = await create_user(override_get_async_session, building_uuid, company_uuid, username=username)
        user_list.append(user)
    return user_list


@pytest.fixture(scope='function')
async def user(override_get_async_session, building) -> UserDB:
    """User fixture."""
    user = await create_user(override_get_async_session, building.uuid, building.company_uuid)
    await create_users(override_get_async_session, building.uuid, building.company_uuid, USER_COUNT - 1)
    return user


@pytest.fixture(scope='function')
async def director(override_get_async_session, building) -> UserDB:
    """Director fixture, belongs to the company of the building fixture."""
    return await create_user(
        override_get_async_session,
        building.uuid,
        building.company_uuid,
        username='director',
        role=UserRole.DIRECTOR,
    )


@pytest.fixture(scope='function')
async def user_without_building(override_get_async_session, building) -> UserDB:
    """Employee of the company that belongs to no building."""
    return await create_user(
        override_get_async_session,
        company_uuid=building.company_uuid,
        username='without_building',
    )


@pytest.fixture(scope='function')
async def colleague_director(override_get_async_session, building) -> UserDB:
    """Second director of the same company."""
    return await create_user(
        override_get_async_session,
        building.uuid,
        building.company_uuid,
        username='colleague_director',
        role=UserRole.DIRECTOR,
    )


@pytest.fixture(scope='function')
async def neighbour(override_get_async_session, second_building) -> UserDB:
    """Employee of another building of the same company."""
    return await create_user(
        override_get_async_session,
        second_building.uuid,
        second_building.company_uuid,
        username='neighbour',
    )


@pytest.fixture(scope='function')
async def other_director(override_get_async_session) -> UserDB:
    """Director fixture of another company."""
    other_building = await create_building(override_get_async_session, name='Склад')
    return await create_user(
        override_get_async_session,
        other_building.uuid,
        other_building.company_uuid,
        username='other_director',
        role=UserRole.DIRECTOR,
    )


@pytest.fixture(scope='function')
async def superuser(override_get_async_session) -> UserDB:
    """Superuser fixture, belongs to no building."""
    return await create_user(override_get_async_session, username='superuser', is_superuser=True)
