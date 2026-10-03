import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.company import NEW_COMPANY

pytestmark = pytest.mark.integration


class TestCaseCompanyCreate(BaseTestCase):
    """Company create test suite."""
    url = '/company/'

    async def test_company_create(self, superuser):
        """Test company create by superuser."""
        response = await self.make_post(self.url, superuser.username, NEW_COMPANY, status.HTTP_201_CREATED)
        assert response['name'] == NEW_COMPANY['name']
        assert response['uuid'] is not None

        created = await self.make_get(f'/company/{response["uuid"]}/', superuser.username)
        assert created['name'] == NEW_COMPANY['name']

    async def test_company_create_401(self, superuser):
        """Test company create by non-authenticated user."""
        await self.make_post(self.url, None, NEW_COMPANY, status.HTTP_401_UNAUTHORIZED)

    async def test_company_create_403(self, user):
        """Test company create by an employee."""
        response = await self.make_post(self.url, user.username, NEW_COMPANY, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_company_create_403_director(self, director):
        """Test company create by a director."""
        response = await self.make_post(self.url, director.username, NEW_COMPANY, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_company_create_422(self, superuser):
        """Test company create without name."""
        data = {'title': NEW_COMPANY['name']}
        await self.make_post(self.url, superuser.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)
