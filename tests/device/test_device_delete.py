import pytest
from starlette import status

from tests.base.base_test import BaseTestCase

pytestmark = pytest.mark.integration


class TestCaseDeviceDelete(BaseTestCase):
    """Device delete test suite."""
    url = '/device/{uuid}/'

    async def test_device_delete_by_director(self, director, device):
        """Test device delete by the director of the company."""
        url = self.url.format(uuid=device.uuid)
        await self.make_delete(url, director.username)
        await self.make_get(url, director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_device_delete(self, superuser, device):
        """Test device delete by superuser."""
        url = self.url.format(uuid=device.uuid)
        await self.make_delete(url, superuser.username)
        await self.make_get(url, superuser.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_device_delete_foreign_device(self, director, foreign_device):
        """Test device delete by a director of another company."""
        url = self.url.format(uuid=foreign_device.uuid)
        await self.make_delete(url, director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_device_delete_401(self, device):
        """Test device delete by non-authenticated user."""
        url = self.url.format(uuid=device.uuid)
        await self.make_delete(url, None, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_device_delete_403(self, user, device):
        """Test device delete by an employee."""
        url = self.url.format(uuid=device.uuid)
        await self.make_delete(url, user.username, status_code=status.HTTP_403_FORBIDDEN)

    async def test_device_delete_404(self, superuser):
        """Test device delete for unknown device."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_delete(url, superuser.username, status_code=status.HTTP_404_NOT_FOUND)
