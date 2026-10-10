import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.threshold import LEVELS, NEW_THRESHOLDS

pytestmark = pytest.mark.integration

NEW_VALUES = ['10.500', '30.000', '75.125', '200.000']


class TestCaseDeviceThresholdCreate(BaseTestCase):
    """Device threshold create test suite."""
    url = '/device/{uuid}/thresholds/'

    async def test_threshold_create_by_director(self, director, device, default_thresholds):
        """Test the director sets thresholds of every level for a device of the company."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_post(url, director.username, NEW_THRESHOLDS, status.HTTP_201_CREATED)
        assert [item['level'] for item in response] == LEVELS
        assert [item['value'] for item in response] == NEW_VALUES
        assert {item['is_default'] for item in response} == {False}

    async def test_threshold_create(self, superuser, device, default_thresholds):
        """Test thresholds set by superuser replace the default ones for the device."""
        url = self.url.format(uuid=device.uuid)
        await self.make_post(url, superuser.username, NEW_THRESHOLDS, status.HTTP_201_CREATED)

        thresholds = await self.make_get(url, superuser.username)
        assert [item['value'] for item in thresholds] == NEW_VALUES
        assert {item['is_default'] for item in thresholds} == {False}

    async def test_threshold_create_without_default(self, director, device):
        """Test thresholds are set for a device while its type has no default ones."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_post(url, director.username, NEW_THRESHOLDS, status.HTTP_201_CREATED)
        assert [item['value'] for item in response] == NEW_VALUES

    async def test_threshold_create_negative_values(self, director, device):
        """Test thresholds are set with negative values."""
        url = self.url.format(uuid=device.uuid)
        data = {'level_1': '-40', 'level_2': '-20.5', 'level_3': '0', 'level_4': '15'}
        response = await self.make_post(url, director.username, data, status.HTTP_201_CREATED)
        assert [item['value'] for item in response] == ['-40.000', '-20.500', '0.000', '15.000']

    async def test_threshold_create_409(self, director, device, device_thresholds):
        """Test thresholds are not set for a device that has them."""
        url = self.url.format(uuid=device.uuid)
        await self.make_post(url, director.username, NEW_THRESHOLDS, status.HTTP_409_CONFLICT)

    @pytest.mark.parametrize('data', [
        {},
        {'level_1': '10', 'level_2': '30', 'level_3': '75'},
        {'level_1': '10', 'level_2': '30', 'level_3': '75', 'level_4': None},
        {'level_1': '10', 'level_2': '30', 'level_3': '75', 'level_4': 'abc'},
        {'level_1': '10', 'level_2': '30', 'level_3': '75', 'level_4': '200.1234'},
        {'level_1': '10', 'level_2': '30', 'level_3': '75', 'level_4': '12345678.123'},
    ])
    async def test_threshold_create_422(self, director, device, data):
        """Test thresholds are not set without a level or with a value out of the stored precision."""
        url = self.url.format(uuid=device.uuid)
        await self.make_post(url, director.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)

    @pytest.mark.parametrize('data', [
        {'level_1': '30', 'level_2': '10', 'level_3': '75', 'level_4': '200'},
        {'level_1': '10', 'level_2': '30', 'level_3': '30', 'level_4': '200'},
        {'level_1': '10', 'level_2': '30', 'level_3': '75', 'level_4': '70'},
    ])
    async def test_threshold_create_422_order(self, director, device, data):
        """Test thresholds are not set unless the value of every level is above the previous one."""
        url = self.url.format(uuid=device.uuid)
        await self.make_post(url, director.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)

    async def test_threshold_create_foreign_device(self, director, foreign_device):
        """Test thresholds are not set for a device of another company."""
        url = self.url.format(uuid=foreign_device.uuid)
        await self.make_post(url, director.username, NEW_THRESHOLDS, status.HTTP_404_NOT_FOUND)

    async def test_threshold_create_401(self, device):
        """Test device thresholds create by non-authenticated user."""
        url = self.url.format(uuid=device.uuid)
        await self.make_post(url, None, NEW_THRESHOLDS, status.HTTP_401_UNAUTHORIZED)

    async def test_threshold_create_403(self, user, device):
        """Test device thresholds create by an employee of that building."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_post(url, user.username, NEW_THRESHOLDS, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_threshold_create_404(self, superuser):
        """Test device thresholds create for unknown device."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_post(url, superuser.username, NEW_THRESHOLDS, status.HTTP_404_NOT_FOUND)
