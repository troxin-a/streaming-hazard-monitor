import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.company import COMPANY_DATA

pytestmark = pytest.mark.integration


class TestCaseCompanyDetail(BaseTestCase):
    """Company detail test suite."""
    url = '/company/{uuid}/'

    async def test_company_detail(self, user, company):
        """Test company detail is available to its employee."""
        url = self.url.format(uuid=company.uuid)
        response = await self.make_get(url, user.username)
        assert response == {'uuid': f'{company.uuid}', 'name': COMPANY_DATA['name']}

    async def test_company_detail_superuser(self, superuser, company):
        """Test company detail is available to superuser."""
        url = self.url.format(uuid=company.uuid)
        response = await self.make_get(url, superuser.username)
        assert response == {'uuid': f'{company.uuid}', 'name': COMPANY_DATA['name']}

    async def test_company_detail_foreign_company(self, user, other_company):
        """Test company detail of a company the user does not belong to."""
        url = self.url.format(uuid=other_company.uuid)
        await self.make_get(url, user.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_company_detail_401(self, company):
        """Test company detail by non-authenticated user."""
        url = self.url.format(uuid=company.uuid)
        await self.make_get(url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_company_detail_404(self, user):
        """Test company detail for unknown company."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_get(url, user.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_company_detail_422(self, user):
        """Test company detail with malformed uuid."""
        url = self.url.format(uuid='not-a-uuid')
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
