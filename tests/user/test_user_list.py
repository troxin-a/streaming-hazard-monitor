import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.conftest import get_url_size
from tests.fixtures.users import USER_COUNT

pytestmark = pytest.mark.integration


class TestCaseUserList(BaseTestCase):
    """User list test suite."""
    url = '/user/'

    @pytest.mark.parametrize('size, page', [(5, 1), (5, 2), (1, 3)])
    async def test_user_list_pagination(self, user, many_users, size, page):
        """Test user list respects page size."""
        url = get_url_size(self.url, size, page)
        response = await self.make_get(url, user.username)
        assert response['total'] == USER_COUNT
        assert len(response['items']) == size

    async def test_user_list_own_building(self, user, many_users, neighbour, other_director):
        """Test an employee sees only the users of their building."""
        response = await self.make_get(self.url, user.username)
        assert response['total'] == USER_COUNT
        assert f'{neighbour.uuid}' not in [item['uuid'] for item in response['items']]

    async def test_user_list_own_company(self, director, many_users, neighbour, other_director):
        """Test a director sees the users of every building of their company."""
        response = await self.make_get(self.url, director.username)
        assert response['total'] == USER_COUNT + 2
        assert f'{neighbour.uuid}' in [item['uuid'] for item in response['items']]

    async def test_user_list_without_building(self, user_without_building, user):
        """Test an employee without a building sees only themselves."""
        response = await self.make_get(self.url, user_without_building.username)
        assert response['total'] == 1
        assert response['items'][0]['uuid'] == f'{user_without_building.uuid}'

    async def test_user_list_superuser(self, superuser, many_users, neighbour, other_director):
        """Test superuser sees every user."""
        response = await self.make_get(self.url, superuser.username)
        assert response['total'] == USER_COUNT + 3

    async def test_user_list_401(self, user):
        """Test user list by non-authenticated user."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_user_list_405(self, user):
        """Test user list wrong request method."""
        await self.make_delete(self.url, user.username, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_user_list_422(self, user):
        """Test user list negative size."""
        url = get_url_size(self.url, -3)
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
