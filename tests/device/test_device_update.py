import pytest
from starlette import status

from shared.device.enums import DeviceType
from tests.base.base_test import BaseTestCase
from tests.fixtures.device import NEW_DEVICE

pytestmark = pytest.mark.integration


class TestCaseDeviceUpdate(BaseTestCase):
    """Device update test suite."""
    url = '/device/{uuid}/'

    async def test_device_update_by_director(self, director, device):
        """Test device update by the director of the company."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_patch(url, director.username, NEW_DEVICE)
        assert response['name'] == NEW_DEVICE['name']
        assert response['serial_number'] == NEW_DEVICE['serial_number']
        assert response['type'] == DeviceType.METHANE.value

    async def test_device_update(self, superuser, device):
        """Test device update by superuser."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_patch(url, superuser.username, {'name': 'Датчик №2'})
        assert response['name'] == 'Датчик №2'
        assert response['type'] == DeviceType.CO.value

    async def test_device_update_building(self, director, device, second_building):
        """Test device is moved to another building of the same company."""
        url = self.url.format(uuid=device.uuid)
        data = {'building_uuid': f'{second_building.uuid}'}
        response = await self.make_patch(url, director.username, data)
        assert response['building']['uuid'] == f'{second_building.uuid}'

    async def test_device_update_foreign_building(self, director, device, other_building):
        """Test device is not moved to a building of another company."""
        url = self.url.format(uuid=device.uuid)
        data = {'building_uuid': f'{other_building.uuid}'}
        response = await self.make_patch(url, director.username, data, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Building not found'

    async def test_device_update_409_taken_serial_number(self, director, device, neighbour_device):
        """Test device update with the serial number of another device."""
        url = self.url.format(uuid=device.uuid)
        data = {'serial_number': neighbour_device.serial_number}
        await self.make_patch(url, director.username, data, status.HTTP_409_CONFLICT)

    async def test_device_update_foreign_device(self, director, foreign_device):
        """Test device update by a director of another company."""
        url = self.url.format(uuid=foreign_device.uuid)
        await self.make_patch(url, director.username, NEW_DEVICE, status.HTTP_404_NOT_FOUND)

    async def test_device_update_401(self, device):
        """Test device update by non-authenticated user."""
        url = self.url.format(uuid=device.uuid)
        await self.make_patch(url, None, NEW_DEVICE, status.HTTP_401_UNAUTHORIZED)

    async def test_device_update_403(self, user, device):
        """Test device update by an employee of that building."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_patch(url, user.username, NEW_DEVICE, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_device_update_404(self, superuser):
        """Test device update for unknown device."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_patch(url, superuser.username, NEW_DEVICE, status.HTTP_404_NOT_FOUND)
