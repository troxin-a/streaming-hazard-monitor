from starlette import status

from tests.base.base_test import BaseTestCase
from tests.conftest import get_url_size


class TestCaseUserList(BaseTestCase):
    """User list test suite."""
    url = '/user/'

    async def test_get_user_list(self, user):
        """Test get user list."""
        response = await self.make_get(self.url, user.username)
        assert len(response['items']) <= response['size']
        assert response['items'][0].get('uuid') is not None

        size = 15
        url = get_url_size(self.url, size)
        response = await self.make_get(url, user.username)
        assert len(response['items']) <= size

        size, page = 1, 2
        url = get_url_size(self.url, size, page)
        response = await self.make_get(url, user.username)
        assert len(response['items']) == size

    async def test_user_list_401(self, user):
        """Test get user list by non-authenticated user."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_user_list_405(self, user):
        """Test user list wrong request method."""
        await self.make_delete(self.url, user.username, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_get_user_list_422(self, user):
        """Test get user list negative size."""
        url = get_url_size(self.url, -3)
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
