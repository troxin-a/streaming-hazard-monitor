import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.conftest import get_url_size
from tests.fixtures.company import COMPANY_COUNT, COMPANY_DATA

pytestmark = pytest.mark.integration


class TestCaseCompanyList(BaseTestCase):
    """Company list test suite."""
    url = '/company/'

    async def test_company_list(self, user, company, many_companies, other_company):
        """Test an employee sees only the company they belong to."""
        response = await self.make_get(self.url, user.username)
        assert response['total'] == 1
        assert response['items'][0]['uuid'] == f'{company.uuid}'
        assert response['items'][0]['name'] == COMPANY_DATA['name']

    @pytest.mark.parametrize('size, page', [(5, 1), (5, 2), (1, 3)])
    async def test_company_list_pagination(self, superuser, many_companies, size, page):
        """Test company list respects page size."""
        url = get_url_size(self.url, size, page)
        response = await self.make_get(url, superuser.username)
        assert response['total'] == COMPANY_COUNT
        assert len(response['items']) == size

    async def test_company_list_superuser(self, superuser, many_companies, other_company):
        """Test superuser sees every company."""
        response = await self.make_get(self.url, superuser.username)
        assert response['total'] == COMPANY_COUNT + 1

    async def test_company_list_search(self, superuser, company, other_company):
        """Test company list is narrowed by a part of the name in any case."""
        url = f'{self.url}?search=северсклад'
        response = await self.make_get(url, superuser.username)
        assert [item['uuid'] for item in response['items']] == [f'{other_company.uuid}']

    async def test_company_list_search_no_match(self, superuser, company):
        """Test company list is empty when no name contains the search text."""
        url = f'{self.url}?search=химпром'
        response = await self.make_get(url, superuser.username)
        assert response['total'] == 0

    async def test_company_list_401(self, user):
        """Test company list by non-authenticated user."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_company_list_422(self, user):
        """Test company list negative size."""
        url = get_url_size(self.url, -1)
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
