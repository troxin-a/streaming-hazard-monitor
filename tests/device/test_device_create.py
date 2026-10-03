import pytest
from starlette import status

from shared.device.enums import DeviceType
from tests.base.base_test import BaseTestCase
from tests.fixtures.device import NEW_DEVICE

pytestmark = pytest.mark.integration


class TestCaseDeviceCreate(BaseTestCase):
    """Device create test suite."""
    url = '/device/'

    async def test_device_create_by_director(self, director, building):
        """Test device create by the director of the company."""
        data = {**NEW_DEVICE, 'building_uuid': f'{building.uuid}'}
        response = await self.make_post(self.url, director.username, data, status.HTTP_201_CREATED)
        assert response['name'] == NEW_DEVICE['name']
        assert response['serial_number'] == NEW_DEVICE['serial_number']
        assert response['type'] == DeviceType.METHANE.value
        assert response['has_api_key'] is False
        assert response['building']['uuid'] == f'{building.uuid}'

    async def test_device_create(self, superuser, building):
        """Test device create by superuser."""
        data = {**NEW_DEVICE, 'building_uuid': f'{building.uuid}'}
        response = await self.make_post(self.url, superuser.username, data, status.HTTP_201_CREATED)
        assert response['building']['uuid'] == f'{building.uuid}'

    async def test_device_create_foreign_building(self, director, other_building):
        """Test device create in a building of another company."""
        data = {**NEW_DEVICE, 'building_uuid': f'{other_building.uuid}'}
        response = await self.make_post(self.url, director.username, data, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Building not found'

    async def test_device_create_401(self, building):
        """Test device create by non-authenticated user."""
        data = {**NEW_DEVICE, 'building_uuid': f'{building.uuid}'}
        await self.make_post(self.url, None, data, status.HTTP_401_UNAUTHORIZED)

    async def test_device_create_403(self, user, building):
        """Test device create by an employee."""
        data = {**NEW_DEVICE, 'building_uuid': f'{building.uuid}'}
        response = await self.make_post(self.url, user.username, data, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_device_create_404(self, superuser):
        """Test device create for unknown building."""
        data = {**NEW_DEVICE, 'building_uuid': self.unknown_uuid}
        await self.make_post(self.url, superuser.username, data, status.HTTP_404_NOT_FOUND)

    async def test_device_create_409_taken_serial_number(self, superuser, device, building):
        """Test device create with the serial number of another device."""
        data = {**NEW_DEVICE, 'serial_number': device.serial_number, 'building_uuid': f'{building.uuid}'}
        await self.make_post(self.url, superuser.username, data, status.HTTP_409_CONFLICT)

    async def test_device_create_422_without_building(self, superuser):
        """Test device create without building."""
        await self.make_post(self.url, superuser.username, NEW_DEVICE, status.HTTP_422_UNPROCESSABLE_CONTENT)

    async def test_device_create_422_without_serial_number(self, superuser, building):
        """Test device create without serial number."""
        data = {'name': NEW_DEVICE['name'], 'type': NEW_DEVICE['type'], 'building_uuid': f'{building.uuid}'}
        await self.make_post(self.url, superuser.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)

    async def test_device_create_422_unknown_type(self, superuser, building):
        """Test device create with a type that is not a sensor type."""
        data = {'name': NEW_DEVICE['name'], 'type': 'teapot', 'building_uuid': f'{building.uuid}'}
        await self.make_post(self.url, superuser.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)
