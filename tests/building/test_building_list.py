import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.conftest import get_url_size
from tests.fixtures.building import BUILDING_COUNT
from tests.fixtures.company import COMPANY_DATA

pytestmark = pytest.mark.integration


class TestCaseBuildingList(BaseTestCase):
    """Building list test suite."""
    url = '/building/'

    async def test_building_list(self, user, building, many_buildings, other_building):
        """Test an employee sees only their own building."""
        response = await self.make_get(self.url, user.username)
        assert response['total'] == 1
        assert response['items'][0]['uuid'] == f'{building.uuid}'
        assert response['items'][0]['company']['name'] == COMPANY_DATA['name']

    @pytest.mark.parametrize('size, page', [(5, 1), (5, 2), (1, 3)])
    async def test_building_list_pagination(self, director, many_buildings, size, page):
        """Test building list respects page size."""
        url = get_url_size(self.url, size, page)
        response = await self.make_get(url, director.username)
        assert response['total'] == BUILDING_COUNT
        assert len(response['items']) == size

    async def test_building_list_without_building(self, user_without_building, building):
        """Test an employee without a building sees no buildings."""
        response = await self.make_get(self.url, user_without_building.username)
        assert response['total'] == 0

    async def test_building_list_own_company(self, director, many_buildings, other_building):
        """Test a director sees every building of their company."""
        response = await self.make_get(self.url, director.username)
        assert response['total'] == BUILDING_COUNT
        assert f'{other_building.uuid}' not in [item['uuid'] for item in response['items']]

    async def test_building_list_superuser(self, superuser, many_buildings, other_building):
        """Test superuser sees every building."""
        response = await self.make_get(self.url, superuser.username)
        assert response['total'] == BUILDING_COUNT + 1

    async def test_building_list_search(self, director, building, second_building):
        """Test building list is narrowed by a part of the name in any case."""
        url = f'{self.url}?search=ОФИ'
        response = await self.make_get(url, director.username)
        assert [item['uuid'] for item in response['items']] == [f'{second_building.uuid}']

    async def test_building_list_search_another_company(self, director, building, other_building):
        """Test building search does not reach the buildings of another company."""
        url = f'{self.url}?search=склад'
        response = await self.make_get(url, director.username)
        assert response['total'] == 0

    async def test_building_list_401(self, user):
        """Test building list by non-authenticated user."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_building_list_422(self, user):
        """Test building list negative size."""
        url = get_url_size(self.url, -1)
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
