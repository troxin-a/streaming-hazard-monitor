import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.building import NEW_BUILDING

pytestmark = pytest.mark.integration


class TestCaseBuildingUpdate(BaseTestCase):
    """Building update test suite."""
    url = '/building/{uuid}/'

    async def test_building_update_by_director(self, director, building, company):
        """Test building update by the director of the company."""
        url = self.url.format(uuid=building.uuid)
        response = await self.make_patch(url, director.username, NEW_BUILDING)
        assert response['name'] == NEW_BUILDING['name']
        assert response['company']['uuid'] == f'{company.uuid}'

    async def test_building_update(self, superuser, building, company):
        """Test building update by superuser."""
        url = self.url.format(uuid=building.uuid)
        response = await self.make_patch(url, superuser.username, NEW_BUILDING)
        assert response['name'] == NEW_BUILDING['name']
        assert response['company']['uuid'] == f'{company.uuid}'

    async def test_building_update_company(self, superuser, building, other_company):
        """Test building is moved to another company by superuser."""
        url = self.url.format(uuid=building.uuid)
        data = {'company_uuid': f'{other_company.uuid}'}
        response = await self.make_patch(url, superuser.username, data)
        assert response['company']['uuid'] == f'{other_company.uuid}'

    async def test_building_update_foreign_company(self, director, building, other_company):
        """Test building is not moved to another company by a director."""
        url = self.url.format(uuid=building.uuid)
        data = {'company_uuid': f'{other_company.uuid}'}
        response = await self.make_patch(url, director.username, data, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Company not found'

    async def test_building_update_foreign_building(self, other_director, building):
        """Test building update by a director of another company."""
        url = self.url.format(uuid=building.uuid)
        await self.make_patch(url, other_director.username, NEW_BUILDING, status.HTTP_404_NOT_FOUND)

    async def test_building_update_401(self, building):
        """Test building update by non-authenticated user."""
        url = self.url.format(uuid=building.uuid)
        await self.make_patch(url, None, NEW_BUILDING, status.HTTP_401_UNAUTHORIZED)

    async def test_building_update_403(self, user, building):
        """Test building update by an employee of that company."""
        url = self.url.format(uuid=building.uuid)
        response = await self.make_patch(url, user.username, NEW_BUILDING, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_building_update_404(self, superuser):
        """Test building update for unknown building."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_patch(url, superuser.username, NEW_BUILDING, status.HTTP_404_NOT_FOUND)
