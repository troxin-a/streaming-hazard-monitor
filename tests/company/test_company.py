import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.conftest import get_url_size
from tests.fixtures.building import COMPANY_DATA

pytestmark = pytest.mark.integration

NEW_COMPANY = {'name': 'ЗАО Химпром'}


class TestCaseCompanyList(BaseTestCase):
    """Company list test suite."""
    url = '/company/'

    async def test_company_list(self, user, building, company):
        """Test an employee sees only the company they belong to."""
        response = await self.make_get(self.url, user.username)
        assert response['total'] == 1
        assert response['items'][0]['uuid'] == f'{building.company_uuid}'
        assert response['items'][0]['name'] == COMPANY_DATA['name']

    async def test_company_list_superuser(self, superuser, building, company):
        """Test superuser sees every company."""
        response = await self.make_get(self.url, superuser.username)
        assert response['total'] == 2

    async def test_company_list_pagination(self, superuser, building, company):
        """Test company list respects page size."""
        url = get_url_size(self.url, 1)
        response = await self.make_get(url, superuser.username)
        assert response['total'] == 2
        assert len(response['items']) == 1

    async def test_company_list_401(self, user):
        """Test company list by non-authenticated user."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_company_list_422(self, user):
        """Test company list negative size."""
        url = get_url_size(self.url, -1)
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


class TestCaseCompanyDetail(BaseTestCase):
    """Company detail test suite."""
    url = '/company/{uuid}/'

    async def test_company_detail(self, user, building):
        """Test company detail is available to its employee."""
        response = await self.make_get(self.url.format(uuid=building.company_uuid), user.username)
        assert response == {'uuid': f'{building.company_uuid}', 'name': COMPANY_DATA['name']}

    async def test_company_detail_superuser(self, superuser, company):
        """Test company detail is available to superuser."""
        response = await self.make_get(self.url.format(uuid=company.uuid), superuser.username)
        assert response == {'uuid': f'{company.uuid}', 'name': COMPANY_DATA['name']}

    async def test_company_detail_foreign_company(self, user, company):
        """Test company detail of a company the user does not belong to."""
        await self.make_get(
            self.url.format(uuid=company.uuid), user.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_company_detail_401(self, company):
        """Test company detail by non-authenticated user."""
        await self.make_get(self.url.format(uuid=company.uuid), status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_company_detail_404(self, user):
        """Test company detail for unknown company."""
        await self.make_get(
            self.url.format(uuid=self.unknown_uuid), user.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_company_detail_422(self, user):
        """Test company detail with malformed uuid."""
        await self.make_get(
            self.url.format(uuid='not-a-uuid'), user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )


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
        await self.make_post(
            self.url, superuser.username, {'title': 'ЗАО Химпром'}, status.HTTP_422_UNPROCESSABLE_CONTENT,
        )


class TestCaseCompanyUpdate(BaseTestCase):
    """Company update test suite."""
    url = '/company/{uuid}/'

    async def test_company_update_by_director(self, director, building):
        """Test company update by its director."""
        response = await self.make_patch(
            self.url.format(uuid=building.company_uuid), director.username, NEW_COMPANY,
        )
        assert response == {'uuid': f'{building.company_uuid}', 'name': NEW_COMPANY['name']}

    async def test_company_update(self, superuser, company):
        """Test company update by superuser."""
        response = await self.make_patch(self.url.format(uuid=company.uuid), superuser.username, NEW_COMPANY)
        assert response == {'uuid': f'{company.uuid}', 'name': NEW_COMPANY['name']}

    async def test_company_update_401(self, company):
        """Test company update by non-authenticated user."""
        await self.make_patch(
            self.url.format(uuid=company.uuid), None, NEW_COMPANY, status.HTTP_401_UNAUTHORIZED,
        )

    async def test_company_update_403(self, user, building):
        """Test company update by an employee of that company."""
        response = await self.make_patch(
            self.url.format(uuid=building.company_uuid), user.username, NEW_COMPANY, status.HTTP_403_FORBIDDEN,
        )
        assert response['detail'] == 'Access denied'

    async def test_company_update_by_foreign_director(self, other_director, building):
        """Test company update by a director of another company."""
        await self.make_patch(
            self.url.format(uuid=building.company_uuid),
            other_director.username,
            NEW_COMPANY,
            status.HTTP_404_NOT_FOUND,
        )

    async def test_company_update_404(self, superuser):
        """Test company update for unknown company."""
        await self.make_patch(
            self.url.format(uuid=self.unknown_uuid), superuser.username, NEW_COMPANY, status.HTTP_404_NOT_FOUND,
        )


class TestCaseCompanyDelete(BaseTestCase):
    """Company delete test suite."""
    url = '/company/{uuid}/'

    async def test_company_delete(self, superuser, company):
        """Test company without buildings is deleted by superuser."""
        await self.make_delete(self.url.format(uuid=company.uuid), superuser.username)
        await self.make_get(
            self.url.format(uuid=company.uuid), superuser.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_company_delete_401(self, company):
        """Test company delete by non-authenticated user."""
        await self.make_delete(
            self.url.format(uuid=company.uuid), None, status_code=status.HTTP_401_UNAUTHORIZED,
        )

    async def test_company_delete_403(self, user, company):
        """Test company delete by an employee."""
        await self.make_delete(
            self.url.format(uuid=company.uuid), user.username, status_code=status.HTTP_403_FORBIDDEN,
        )

    async def test_company_delete_403_director(self, director, building):
        """Test company delete by its director."""
        await self.make_delete(
            self.url.format(uuid=building.company_uuid), director.username, status_code=status.HTTP_403_FORBIDDEN,
        )

    async def test_company_delete_404(self, superuser):
        """Test company delete for unknown company."""
        await self.make_delete(
            self.url.format(uuid=self.unknown_uuid), superuser.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_company_delete_409(self, superuser, building):
        """Test company with buildings is not deleted."""
        await self.make_delete(
            self.url.format(uuid=building.company_uuid), superuser.username, status_code=status.HTTP_409_CONFLICT,
        )
