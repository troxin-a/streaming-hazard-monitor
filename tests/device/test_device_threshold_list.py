import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.threshold import LEVELS

pytestmark = pytest.mark.integration


class TestCaseDeviceThresholdList(BaseTestCase):
    """Device threshold list test suite."""
    url = '/device/{uuid}/thresholds/'

    async def test_threshold_list_default(self, user, device, default_thresholds):
        """Test a device without its own thresholds has the default ones of its type."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_get(url, user.username)
        assert [item['level'] for item in response] == LEVELS
        assert [item['value'] for item in response] == ['20.000', '50.000', '100.000', '300.000']
        assert {item['is_default'] for item in response} == {True}

    async def test_threshold_list(self, user, device, default_thresholds, device_thresholds):
        """Test a device with its own thresholds has them instead of the default ones."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_get(url, user.username)
        assert [item['level'] for item in response] == LEVELS
        assert [item['value'] for item in response] == ['25.000', '60.000', '120.000', '350.000']
        assert {item['is_default'] for item in response} == {False}

    async def test_threshold_list_another_type(self, user, device, methane_default_thresholds):
        """Test a device has no thresholds while its type has no default ones."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_get(url, user.username)
        assert response == []

    async def test_threshold_list_another_building(self, user, neighbour_device, default_thresholds):
        """Test an employee does not see the thresholds of a device of another building."""
        url = self.url.format(uuid=neighbour_device.uuid)
        await self.make_get(url, user.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_threshold_list_foreign_device(self, director, foreign_device, foreign_device_thresholds):
        """Test a director does not see the thresholds of a device of another company."""
        url = self.url.format(uuid=foreign_device.uuid)
        await self.make_get(url, director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_threshold_list_401(self, device, default_thresholds):
        """Test device thresholds list by non-authenticated user."""
        url = self.url.format(uuid=device.uuid)
        await self.make_get(url, None, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_threshold_list_404(self, superuser, default_thresholds):
        """Test device thresholds list for unknown device."""
        url = self.url.format(uuid=self.unknown_uuid)
        response = await self.make_get(url, superuser.username, status_code=status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Device not found'
