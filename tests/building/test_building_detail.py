import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.building import BUILDING_DATA
from tests.fixtures.company import COMPANY_DATA

pytestmark = pytest.mark.integration


class TestCaseBuildingDetail(BaseTestCase):
    """Building detail test suite."""
    url = '/building/{uuid}/'

    async def test_building_detail(self, user, building, company):
        """Test building detail returns its company."""
        url = self.url.format(uuid=building.uuid)
        response = await self.make_get(url, user.username)
        assert response['uuid'] == f'{building.uuid}'
        assert response['name'] == BUILDING_DATA['name']
        assert response['company'] == {'uuid': f'{company.uuid}', 'name': COMPANY_DATA['name']}

    async def test_building_detail_another_building(self, user, second_building):
        """Test building detail of another building of the same company."""
        url = self.url.format(uuid=second_building.uuid)
        await self.make_get(url, user.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_detail_another_building_by_director(self, director, second_building):
        """Test building detail of another building of the same company by its director."""
        url = self.url.format(uuid=second_building.uuid)
        response = await self.make_get(url, director.username)
        assert response['uuid'] == f'{second_building.uuid}'

    async def test_building_detail_foreign_company(self, user, other_building):
        """Test building detail of another company."""
        url = self.url.format(uuid=other_building.uuid)
        await self.make_get(url, user.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_detail_401(self, building):
        """Test building detail by non-authenticated user."""
        url = self.url.format(uuid=building.uuid)
        await self.make_get(url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_building_detail_404(self, user):
        """Test building detail for unknown building."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_get(url, user.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_detail_422(self, user):
        """Test building detail with malformed uuid."""
        url = self.url.format(uuid='not-a-uuid')
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
