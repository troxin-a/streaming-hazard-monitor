import pytest
from starlette import status

from shared.device.enums import DeviceType
from tests.base.base_test import BaseTestCase
from tests.fixtures.device import DEVICE_DATA

pytestmark = pytest.mark.integration


class TestCaseDeviceDetail(BaseTestCase):
    """Device detail test suite."""
    url = '/device/{uuid}/'

    async def test_device_detail(self, user, device, building):
        """Test device detail returns its building."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_get(url, user.username)
        assert response['uuid'] == f'{device.uuid}'
        assert response['name'] == DEVICE_DATA['name']
        assert response['serial_number'] == DEVICE_DATA['serial_number']
        assert response['type'] == DeviceType.CO.value
        assert response['has_api_key'] is False
        assert response['building']['uuid'] == f'{building.uuid}'

    async def test_device_detail_with_api_key(self, user, device_with_api_key):
        """Test device detail reports the issued api key without exposing the key or its hash."""
        url = self.url.format(uuid=device_with_api_key.uuid)
        response = await self.make_get(url, user.username)
        assert response['has_api_key'] is True
        assert 'key' not in response
        assert 'key_hash' not in response

    async def test_device_detail_another_building(self, user, neighbour_device):
        """Test device detail of another building of the same company."""
        url = self.url.format(uuid=neighbour_device.uuid)
        await self.make_get(url, user.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_device_detail_another_building_by_director(self, director, neighbour_device):
        """Test device detail of another building of the same company by its director."""
        url = self.url.format(uuid=neighbour_device.uuid)
        response = await self.make_get(url, director.username)
        assert response['uuid'] == f'{neighbour_device.uuid}'

    async def test_device_detail_foreign_company(self, director, foreign_device):
        """Test device detail of another company."""
        url = self.url.format(uuid=foreign_device.uuid)
        await self.make_get(url, director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_device_detail_401(self, device):
        """Test device detail by non-authenticated user."""
        url = self.url.format(uuid=device.uuid)
        await self.make_get(url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_device_detail_404(self, user):
        """Test device detail for unknown device."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_get(url, user.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_device_detail_422(self, user):
        """Test device detail with malformed uuid."""
        url = self.url.format(uuid='not-a-uuid')
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
