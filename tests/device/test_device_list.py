import pytest
from starlette import status

from shared.device.enums import DeviceType
from tests.base.base_test import BaseTestCase
from tests.conftest import get_url_size
from tests.fixtures.building import BUILDING_DATA
from tests.fixtures.device import DEVICE_COUNT

pytestmark = pytest.mark.integration


class TestCaseDeviceList(BaseTestCase):
    """Device list test suite."""
    url = '/device/'

    async def test_device_list(self, user, many_devices, foreign_device):
        """Test an employee sees only the devices of their building."""
        response = await self.make_get(self.url, user.username)
        assert response['total'] == DEVICE_COUNT
        assert {item['type'] for item in response['items']} == {DeviceType.CO.value}
        assert {item['building']['name'] for item in response['items']} == {BUILDING_DATA['name']}

    @pytest.mark.parametrize('size, page', [(5, 1), (5, 2), (1, 3)])
    async def test_device_list_pagination(self, user, many_devices, size, page):
        """Test device list respects page size."""
        url = get_url_size(self.url, size, page)
        response = await self.make_get(url, user.username)
        assert response['total'] == DEVICE_COUNT
        assert len(response['items']) == size

    async def test_device_list_another_building(self, user, device, neighbour_device):
        """Test an employee does not see the devices of another building of their company."""
        response = await self.make_get(self.url, user.username)
        assert response['total'] == 1
        assert response['items'][0]['uuid'] == f'{device.uuid}'

    async def test_device_list_without_building(self, user_without_building, device):
        """Test an employee without a building sees no devices."""
        response = await self.make_get(self.url, user_without_building.username)
        assert response['total'] == 0

    async def test_device_list_own_company(self, director, device, neighbour_device, foreign_device):
        """Test a director sees every device of their company."""
        response = await self.make_get(self.url, director.username)
        assert response['total'] == 2
        assert f'{foreign_device.uuid}' not in [item['uuid'] for item in response['items']]

    async def test_device_list_superuser(self, superuser, device, neighbour_device, foreign_device):
        """Test superuser sees every device."""
        response = await self.make_get(self.url, superuser.username)
        assert response['total'] == 3

    async def test_device_list_has_api_key(self, user, device, device_with_api_key):
        """Test device list reports which devices have an issued api key."""
        response = await self.make_get(self.url, user.username)
        has_api_key = {item['uuid']: item['has_api_key'] for item in response['items']}
        assert has_api_key == {f'{device.uuid}': False, f'{device_with_api_key.uuid}': True}

    @pytest.mark.parametrize('search', ['ДЫМ', 'sn-0002'])
    async def test_device_list_search(self, director, device, neighbour_device, search):
        """Test device list is narrowed by a part of the name or the serial number in any case."""
        url = f'{self.url}?search={search}'
        response = await self.make_get(url, director.username)
        assert [item['uuid'] for item in response['items']] == [f'{neighbour_device.uuid}']

    async def test_device_list_search_another_company(self, director, device, foreign_device):
        """Test device search does not reach the devices of another company."""
        url = f'{self.url}?search=метан'
        response = await self.make_get(url, director.username)
        assert response['total'] == 0

    async def test_device_list_401(self, device):
        """Test device list by non-authenticated user."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_device_list_422(self, user):
        """Test device list negative size."""
        url = get_url_size(self.url, -1)
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
