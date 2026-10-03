import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.device import API_KEY

pytestmark = pytest.mark.integration


class TestCaseDeviceAPIKeyCreate(BaseTestCase):
    """Device api key issue test suite."""
    url = '/device/{uuid}/api-key/'

    async def test_api_key_create_by_director(self, director, device):
        """Test api key issue by the director of the company."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_post(url, director.username, {}, status.HTTP_201_CREATED)
        assert response['key']

        detail = await self.make_get(f'/device/{device.uuid}/', director.username)
        assert detail['has_api_key'] is True

    async def test_api_key_create(self, superuser, device):
        """Test api key issue by superuser."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_post(url, superuser.username, {}, status.HTTP_201_CREATED)
        assert response['key']

    async def test_api_key_create_twice(self, director, device_with_api_key):
        """Test api key is not reissued while the device has a live one."""
        url = self.url.format(uuid=device_with_api_key.uuid)
        response = await self.make_post(url, director.username, {}, status.HTTP_409_CONFLICT)
        assert response['detail'] == 'Device already has an api key'

    async def test_api_key_create_after_revoke(self, director, device_with_api_key):
        """Test api key is issued again after the previous one is revoked."""
        url = self.url.format(uuid=device_with_api_key.uuid)
        await self.make_delete(url, director.username)

        response = await self.make_post(url, director.username, {}, status.HTTP_201_CREATED)
        assert response['key']
        assert response['key'] != API_KEY

    async def test_api_key_create_foreign_device(self, director, foreign_device):
        """Test api key issue for a device of another company."""
        url = self.url.format(uuid=foreign_device.uuid)
        await self.make_post(url, director.username, {}, status.HTTP_404_NOT_FOUND)

    async def test_api_key_create_401(self, device):
        """Test api key issue by non-authenticated user."""
        url = self.url.format(uuid=device.uuid)
        await self.make_post(url, None, {}, status.HTTP_401_UNAUTHORIZED)

    async def test_api_key_create_403(self, user, device):
        """Test api key issue by an employee."""
        url = self.url.format(uuid=device.uuid)
        response = await self.make_post(url, user.username, {}, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_api_key_create_404(self, superuser):
        """Test api key issue for unknown device."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_post(url, superuser.username, {}, status.HTTP_404_NOT_FOUND)
