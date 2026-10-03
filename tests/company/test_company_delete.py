import pytest
from starlette import status

from tests.base.base_test import BaseTestCase

pytestmark = pytest.mark.integration


class TestCaseCompanyDelete(BaseTestCase):
    """Company delete test suite."""
    url = '/company/{uuid}/'

    async def test_company_delete(self, superuser, company):
        """Test company without buildings is deleted by superuser."""
        url = self.url.format(uuid=company.uuid)
        await self.make_delete(url, superuser.username)
        await self.make_get(url, superuser.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_company_delete_401(self, company):
        """Test company delete by non-authenticated user."""
        url = self.url.format(uuid=company.uuid)
        await self.make_delete(url, None, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_company_delete_403(self, user, company):
        """Test company delete by an employee."""
        url = self.url.format(uuid=company.uuid)
        await self.make_delete(url, user.username, status_code=status.HTTP_403_FORBIDDEN)

    async def test_company_delete_403_director(self, director, company):
        """Test company delete by its director."""
        url = self.url.format(uuid=company.uuid)
        await self.make_delete(url, director.username, status_code=status.HTTP_403_FORBIDDEN)

    async def test_company_delete_404(self, superuser):
        """Test company delete for unknown company."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_delete(url, superuser.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_company_delete_409(self, superuser, building, company):
        """Test company with buildings is not deleted."""
        url = self.url.format(uuid=company.uuid)
        await self.make_delete(url, superuser.username, status_code=status.HTTP_409_CONFLICT)
