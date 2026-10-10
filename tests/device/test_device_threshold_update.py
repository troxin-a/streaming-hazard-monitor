import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.threshold import LEVELS, NEW_THRESHOLDS

pytestmark = pytest.mark.integration

NEW_VALUES = ['10.500', '30.000', '75.125', '200.000']


class TestCaseDeviceThresholdUpdate(BaseTestCase):
    """Device threshold update test suite."""
    url = '/device/{uuid}/thresholds/'

    async def test_threshold_update_by_director(self, director, device, device_thresholds):
        """Test thresholds update by the director of the company."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_patch(url, director.username, NEW_THRESHOLDS)
        assert [item['level'] for item in response] == LEVELS
        assert [item['value'] for item in response] == NEW_VALUES
        assert {item['is_default'] for item in response} == {False}

    async def test_threshold_update(self, superuser, device, device_thresholds):
        """Test thresholds updated by superuser are the thresholds of the device."""
        url = self.url.format(uuid=device.uuid)
        await self.make_patch(url, superuser.username, NEW_THRESHOLDS)

        thresholds = await self.make_get(url, superuser.username)
        assert [item['value'] for item in thresholds] == NEW_VALUES

    @pytest.mark.parametrize('data', [
        {},
        {'level_1': '10', 'level_2': '30', 'level_3': '75'},
        {'level_1': '10', 'level_2': '30', 'level_3': '75', 'level_4': None},
        {'level_1': '10', 'level_2': '30', 'level_3': '75', 'level_4': '200.1234'},
    ])
    async def test_threshold_update_422(self, director, device, device_thresholds, data):
        """Test thresholds are not updated without a level or with a value out of the stored precision."""
        url = self.url.format(uuid=device.uuid)
        await self.make_patch(url, director.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)

    @pytest.mark.parametrize('data', [
        {'level_1': '30', 'level_2': '10', 'level_3': '75', 'level_4': '200'},
        {'level_1': '10', 'level_2': '30', 'level_3': '75', 'level_4': '75'},
    ])
    async def test_threshold_update_422_order(self, director, device, device_thresholds, data):
        """Test thresholds are not updated unless the value of every level is above the previous one."""
        url = self.url.format(uuid=device.uuid)
        await self.make_patch(url, director.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)

    async def test_threshold_update_without_thresholds(self, director, device, default_thresholds):
        """Test thresholds update for a device that has only the default thresholds."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_patch(url, director.username, NEW_THRESHOLDS, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Thresholds not found'

    async def test_threshold_update_foreign_device(self, director, foreign_device, foreign_device_thresholds):
        """Test thresholds update for a device of another company."""
        url = self.url.format(uuid=foreign_device.uuid)
        await self.make_patch(url, director.username, NEW_THRESHOLDS, status.HTTP_404_NOT_FOUND)

    async def test_threshold_update_401(self, device, device_thresholds):
        """Test thresholds update by non-authenticated user."""
        url = self.url.format(uuid=device.uuid)
        await self.make_patch(url, None, NEW_THRESHOLDS, status.HTTP_401_UNAUTHORIZED)

    async def test_threshold_update_403(self, user, device, device_thresholds):
        """Test thresholds update by an employee of that building."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_patch(url, user.username, NEW_THRESHOLDS, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_threshold_update_404(self, superuser):
        """Test thresholds update for unknown device."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_patch(url, superuser.username, NEW_THRESHOLDS, status.HTTP_404_NOT_FOUND)
