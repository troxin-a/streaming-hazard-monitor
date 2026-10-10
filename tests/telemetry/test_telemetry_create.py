import json

import pytest
from httpx import ASGITransport
from starlette import status

from receiver.main import app
from shared.config.settings import config
from tests.base.base_test import BaseTestCase
from tests.fixtures.device import API_KEY

pytestmark = pytest.mark.integration


class TestCaseTelemetryCreate(BaseTestCase):
    """Telemetry send test suite."""
    base_url = 'http://test/receiver'
    transport = ASGITransport(app=app)
    url = '/telemetry/'
    headers = {'X-API-Key': API_KEY}

    async def test_telemetry_create(self, device_with_api_key, telemetry_producer):
        """Test reading is accepted for the device the api key belongs to."""
        response = await self.make_post(self.url, None, {'value': '37.5'}, status.HTTP_202_ACCEPTED, self.headers)
        assert response['device_uuid'] == str(device_with_api_key.uuid)
        assert response['value'] == '37.5'
        assert response['received_at']

    async def test_telemetry_create_message(self, device_with_api_key, telemetry_producer):
        """Test accepted reading is sent to the readings topic with the device uuid as the key."""
        response = await self.make_post(self.url, None, {'value': '37.5'}, status.HTTP_202_ACCEPTED, self.headers)
        telemetry_producer.send_and_wait.assert_awaited_once()
        topic, value, key = telemetry_producer.send_and_wait.await_args.args
        assert topic == config.kafka.KAFKA_TOPIC_SENSOR_READINGS
        assert key == str(device_with_api_key.uuid).encode()
        assert json.loads(value) == response

    async def test_telemetry_create_negative_value(self, device_with_api_key, telemetry_producer):
        """Test reading with a negative value is accepted."""
        response = await self.make_post(self.url, None, {'value': '-12.345'}, status.HTTP_202_ACCEPTED, self.headers)
        assert response['value'] == '-12.345'

    async def test_telemetry_create_without_api_key(self, device_with_api_key, telemetry_producer):
        """Test reading is rejected without an api key."""
        response = await self.make_post(self.url, None, {'value': '37.5'}, status.HTTP_401_UNAUTHORIZED)
        assert response['detail'] == 'Api key is required'
        telemetry_producer.send_and_wait.assert_not_awaited()

    async def test_telemetry_create_unknown_api_key(self, device_with_api_key, telemetry_producer):
        """Test reading is rejected with an api key no device has."""
        headers = {'X-API-Key': 'unknown-api-key'}
        response = await self.make_post(self.url, None, {'value': '37.5'}, status.HTTP_401_UNAUTHORIZED, headers)
        assert response['detail'] == 'Invalid api key'
        telemetry_producer.send_and_wait.assert_not_awaited()

    @pytest.mark.parametrize('data', [
        {},
        {'value': 'abc'},
        {'value': '1.2345'},
        {'value': '12345678.123'},
    ])
    async def test_telemetry_create_invalid_value(self, device_with_api_key, telemetry_producer, data):
        """Test reading is rejected without a value or with a value out of the accepted precision."""
        await self.make_post(self.url, None, data, status.HTTP_422_UNPROCESSABLE_CONTENT, self.headers)
        telemetry_producer.send_and_wait.assert_not_awaited()
