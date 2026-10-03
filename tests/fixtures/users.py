from uuid import UUID

import pytest

from shared import UserDB
from shared.user.enums import UserRole
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
    user_list = [
        UserDB(
            building_uuid=building_uuid,
            company_uuid=company_uuid,
            **{**USER_DATA, 'username': f'{USER_DATA["username"]}{number}'},
        )
        for number in range(count)
    ]
    override_get_async_session.add_all(user_list)
    await override_get_async_session.commit()
    return user_list


@pytest.fixture(scope='function')
async def user(override_get_async_session, building, company) -> UserDB:
    """Employee of the building fixture."""
    return await create_user(override_get_async_session, building.uuid, company.uuid)


@pytest.fixture(scope='function')
async def many_users(override_get_async_session, user, building, company) -> list[UserDB]:
    """Employees that bring the total of the building fixture with the user fixture to USER_COUNT."""
    return await create_users(override_get_async_session, building.uuid, company.uuid, USER_COUNT - 1)


@pytest.fixture(scope='function')
async def director(override_get_async_session, building, company) -> UserDB:
    """Director of the company fixture."""
    return await create_user(
        override_get_async_session,
        building.uuid,
        company.uuid,
        username='director',
        role=UserRole.DIRECTOR,
    )


@pytest.fixture(scope='function')
async def user_without_building(override_get_async_session, company) -> UserDB:
    """Employee of the company fixture that belongs to no building."""
    return await create_user(
        override_get_async_session,
        company_uuid=company.uuid,
        username='without_building',
    )


@pytest.fixture(scope='function')
async def colleague_director(override_get_async_session, building, company) -> UserDB:
    """Second director of the company fixture."""
    return await create_user(
        override_get_async_session,
        building.uuid,
        company.uuid,
        username='colleague_director',
        role=UserRole.DIRECTOR,
    )


@pytest.fixture(scope='function')
async def neighbour(override_get_async_session, second_building, company) -> UserDB:
    """Employee of another building of the company fixture."""
    return await create_user(
        override_get_async_session,
        second_building.uuid,
        company.uuid,
        username='neighbour',
    )


@pytest.fixture(scope='function')
async def other_director(override_get_async_session, other_building, other_company) -> UserDB:
    """Director of another company."""
    return await create_user(
        override_get_async_session,
        other_building.uuid,
        other_company.uuid,
        username='other_director',
        role=UserRole.DIRECTOR,
    )


@pytest.fixture(scope='function')
async def superuser(override_get_async_session) -> UserDB:
    """Superuser fixture, belongs to no building."""
    return await create_user(override_get_async_session, username='superuser', is_superuser=True)
