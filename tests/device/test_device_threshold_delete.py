import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.threshold import LEVELS

pytestmark = pytest.mark.integration


class TestCaseDeviceThresholdDelete(BaseTestCase):
    """Device threshold delete test suite."""
    url = '/device/{uuid}/thresholds/'

    async def test_threshold_delete_by_director(self, director, device, default_thresholds, device_thresholds):
        """Test a device has the default thresholds after the director deletes its own ones."""
        url = self.url.format(uuid=device.uuid)
        await self.make_delete(url, director.username)

        thresholds = await self.make_get(url, director.username)
        assert [item['level'] for item in thresholds] == LEVELS
        assert [item['value'] for item in thresholds] == ['20.000', '50.000', '100.000', '300.000']
        assert {item['is_default'] for item in thresholds} == {True}

    async def test_threshold_delete(self, superuser, device, device_thresholds):
        """Test thresholds delete by superuser."""
        url = self.url.format(uuid=device.uuid)
        await self.make_delete(url, superuser.username)

        thresholds = await self.make_get(url, superuser.username)
        assert thresholds == []

    async def test_threshold_delete_without_thresholds(self, director, device, default_thresholds):
        """Test thresholds delete for a device that has only the default thresholds."""
        url = self.url.format(uuid=device.uuid)
        await self.make_delete(url, director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_threshold_delete_foreign_device(self, director, foreign_device, foreign_device_thresholds):
        """Test thresholds delete for a device of another company."""
        url = self.url.format(uuid=foreign_device.uuid)
        await self.make_delete(url, director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_threshold_delete_401(self, device, device_thresholds):
        """Test thresholds delete by non-authenticated user."""
        url = self.url.format(uuid=device.uuid)
        await self.make_delete(url, None, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_threshold_delete_403(self, user, device, device_thresholds):
        """Test thresholds delete by an employee of that building."""
        url = self.url.format(uuid=device.uuid)
        await self.make_delete(url, user.username, status_code=status.HTTP_403_FORBIDDEN)

    async def test_threshold_delete_404(self, superuser):
        """Test thresholds delete for unknown device."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_delete(url, superuser.username, status_code=status.HTTP_404_NOT_FOUND)
