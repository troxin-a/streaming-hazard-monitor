import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.building import NEW_BUILDING
from tests.fixtures.company import COMPANY_DATA

pytestmark = pytest.mark.integration


class TestCaseBuildingCreate(BaseTestCase):
    """Building create test suite."""
    url = '/building/'

    async def test_building_create_by_director(self, director, company):
        """Test building create by the director of the company."""
        data = {**NEW_BUILDING, 'company_uuid': f'{company.uuid}'}
        response = await self.make_post(self.url, director.username, data, status.HTTP_201_CREATED)
        assert response['name'] == NEW_BUILDING['name']
        assert response['company']['uuid'] == f'{company.uuid}'

    async def test_building_create(self, superuser, company):
        """Test building create by superuser."""
        data = {**NEW_BUILDING, 'company_uuid': f'{company.uuid}'}
        response = await self.make_post(self.url, superuser.username, data, status.HTTP_201_CREATED)
        assert response['name'] == NEW_BUILDING['name']
        assert response['company'] == {'uuid': f'{company.uuid}', 'name': COMPANY_DATA['name']}

    async def test_building_create_foreign_company(self, director, other_company):
        """Test building create in another company."""
        data = {**NEW_BUILDING, 'company_uuid': f'{other_company.uuid}'}
        response = await self.make_post(self.url, director.username, data, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Company not found'

    async def test_building_create_401(self, company):
        """Test building create by non-authenticated user."""
        data = {**NEW_BUILDING, 'company_uuid': f'{company.uuid}'}
        await self.make_post(self.url, None, data, status.HTTP_401_UNAUTHORIZED)

    async def test_building_create_403(self, user, company):
        """Test building create by an employee."""
        data = {**NEW_BUILDING, 'company_uuid': f'{company.uuid}'}
        response = await self.make_post(self.url, user.username, data, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_building_create_404(self, superuser):
        """Test building create for unknown company."""
        data = {**NEW_BUILDING, 'company_uuid': self.unknown_uuid}
        await self.make_post(self.url, superuser.username, data, status.HTTP_404_NOT_FOUND)

    async def test_building_create_422(self, superuser):
        """Test building create without company."""
        await self.make_post(self.url, superuser.username, NEW_BUILDING, status.HTTP_422_UNPROCESSABLE_CONTENT)
