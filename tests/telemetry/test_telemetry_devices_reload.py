import pytest
from httpx import ASGITransport
from starlette import status

from receiver.main import app
from receiver.services import reload_devices
from tests.base.base_test import BaseTestCase
from tests.fixtures.device import API_KEY

pytestmark = pytest.mark.integration


class TestCaseTelemetryDevicesReload(BaseTestCase):
    """Reload of the receiver devices test suite."""
    base_url = 'http://test/receiver'
    transport = ASGITransport(app=app)
    url = '/telemetry/'
    headers = {'X-API-Key': API_KEY}

    async def test_telemetry_devices_reload_issued_key(
            self, override_get_async_session, empty_device_keys, device_with_api_key, telemetry_producer,
    ):
        """Test reading is accepted with the key issued after the receiver loaded the devices."""
        await reload_devices(override_get_async_session, empty_device_keys)
        response = await self.make_post(self.url, None, {'value': '37.5'}, status.HTTP_202_ACCEPTED, self.headers)
        assert response['device_uuid'] == str(device_with_api_key.uuid)

    async def test_telemetry_devices_reload_removed_device(
            self, override_get_async_session, stale_device_keys, telemetry_producer,
    ):
        """Test reading is rejected with the key of the device removed after the receiver loaded the devices."""
        await reload_devices(override_get_async_session, stale_device_keys)
        response = await self.make_post(self.url, None, {'value': '37.5'}, status.HTTP_401_UNAUTHORIZED, self.headers)
        assert response['detail'] == 'Invalid api key'
        telemetry_producer.send_and_wait.assert_not_awaited()
