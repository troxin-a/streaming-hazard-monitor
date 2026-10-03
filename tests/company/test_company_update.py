import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.company import NEW_COMPANY

pytestmark = pytest.mark.integration


class TestCaseCompanyUpdate(BaseTestCase):
    """Company update test suite."""
    url = '/company/{uuid}/'

    async def test_company_update_by_director(self, director, company):
        """Test company update by its director."""
        url = self.url.format(uuid=company.uuid)
        response = await self.make_patch(url, director.username, NEW_COMPANY)
        assert response == {'uuid': f'{company.uuid}', 'name': NEW_COMPANY['name']}

    async def test_company_update(self, superuser, company):
        """Test company update by superuser."""
        url = self.url.format(uuid=company.uuid)
        response = await self.make_patch(url, superuser.username, NEW_COMPANY)
        assert response == {'uuid': f'{company.uuid}', 'name': NEW_COMPANY['name']}

    async def test_company_update_401(self, company):
        """Test company update by non-authenticated user."""
        url = self.url.format(uuid=company.uuid)
        await self.make_patch(url, None, NEW_COMPANY, status.HTTP_401_UNAUTHORIZED)

    async def test_company_update_403(self, user, company):
        """Test company update by an employee of that company."""
        url = self.url.format(uuid=company.uuid)
        response = await self.make_patch(url, user.username, NEW_COMPANY, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_company_update_by_foreign_director(self, other_director, company):
        """Test company update by a director of another company."""
        url = self.url.format(uuid=company.uuid)
        await self.make_patch(url, other_director.username, NEW_COMPANY, status.HTTP_404_NOT_FOUND)

    async def test_company_update_404(self, superuser):
        """Test company update for unknown company."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_patch(url, superuser.username, NEW_COMPANY, status.HTTP_404_NOT_FOUND)
