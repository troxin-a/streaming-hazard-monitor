import pytest
from starlette import status

from tests.base.base_test import BaseTestCase

pytestmark = pytest.mark.integration


class TestCaseDeviceAPIKeyDelete(BaseTestCase):
    """Device api key revoke test suite."""
    url = '/device/{uuid}/api-key/'

    async def test_api_key_delete_by_director(self, director, device_with_api_key):
        """Test api key revoke by the director of the company."""
        url = self.url.format(uuid=device_with_api_key.uuid)
        await self.make_delete(url, director.username)

        detail = await self.make_get(f'/device/{device_with_api_key.uuid}/', director.username)
        assert detail['has_api_key'] is False

    async def test_api_key_delete(self, superuser, device_with_api_key):
        """Test api key revoke by superuser."""
        url = self.url.format(uuid=device_with_api_key.uuid)
        await self.make_delete(url, superuser.username)

        detail = await self.make_get(f'/device/{device_with_api_key.uuid}/', superuser.username)
        assert detail['has_api_key'] is False

    async def test_api_key_delete_without_key(self, director, device):
        """Test api key revoke for a device that has no key."""
        url = self.url.format(uuid=device.uuid)
        await self.make_delete(url, director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_api_key_delete_foreign_device(self, director, foreign_device):
        """Test api key revoke for a device of another company."""
        url = self.url.format(uuid=foreign_device.uuid)
        await self.make_delete(url, director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_api_key_delete_401(self, device_with_api_key):
        """Test api key revoke by non-authenticated user."""
        url = self.url.format(uuid=device_with_api_key.uuid)
        await self.make_delete(url, None, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_api_key_delete_403(self, user, device_with_api_key):
        """Test api key revoke by an employee."""
        url = self.url.format(uuid=device_with_api_key.uuid)
        await self.make_delete(url, user.username, status_code=status.HTTP_403_FORBIDDEN)

    async def test_api_key_delete_404(self, superuser):
        """Test api key revoke for unknown device."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_delete(url, superuser.username, status_code=status.HTTP_404_NOT_FOUND)
