import pytest
from httpx import ASGITransport
from starlette import status

from receiver.main import app
from tests.base.base_test import BaseTestCase
from tests.fixtures.device import API_KEY

pytestmark = pytest.mark.integration


class TestCaseTelemetryCreate(BaseTestCase):
    """Telemetry send test suite."""
    base_url = 'http://test/receiver'
    transport = ASGITransport(app=app)
    url = '/telemetry/'
    headers = {'X-API-Key': API_KEY}

    async def test_telemetry_create(self, device_with_api_key):
        """Test reading is saved for the device the api key belongs to."""
        response = await self.make_post(self.url, None, {'value': '37.5'}, status.HTTP_201_CREATED, self.headers)
        assert response['uuid']
        assert response['device_uuid'] == str(device_with_api_key.uuid)
        assert response['value'] == '37.5'
        assert response['created_at']

    async def test_telemetry_create_negative_value(self, device_with_api_key):
        """Test reading with a negative value is saved."""
        response = await self.make_post(self.url, None, {'value': '-12.345'}, status.HTTP_201_CREATED, self.headers)
        assert response['value'] == '-12.345'

    async def test_telemetry_create_without_api_key(self, device_with_api_key):
        """Test reading is rejected without an api key."""
        response = await self.make_post(self.url, None, {'value': '37.5'}, status.HTTP_401_UNAUTHORIZED)
        assert response['detail'] == 'Api key is required'

    async def test_telemetry_create_unknown_api_key(self, device_with_api_key):
        """Test reading is rejected with an api key no device has."""
        headers = {'X-API-Key': 'unknown-api-key'}
        response = await self.make_post(self.url, None, {'value': '37.5'}, status.HTTP_401_UNAUTHORIZED, headers)
        assert response['detail'] == 'Invalid api key'

    @pytest.mark.parametrize('data', [
        {},
        {'value': 'abc'},
        {'value': '1.2345'},
        {'value': '12345678.123'},
    ])
    async def test_telemetry_create_invalid_value(self, device_with_api_key, data):
        """Test reading is rejected without a value or with a value out of the stored precision."""
        await self.make_post(self.url, None, data, status.HTTP_422_UNPROCESSABLE_CONTENT, self.headers)
