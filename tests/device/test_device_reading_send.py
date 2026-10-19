from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.device.services import send_readings
from api.device.websocket import DeviceWebSockets
from tests.fixtures.reading import build_reading, DEVICE_UUID, SECOND_DEVICE_UUID, UNKNOWN_DEVICE_UUID

pytestmark = pytest.mark.unit


def build_websocket() -> MagicMock:
    """Build the open websocket."""
    websocket = MagicMock()
    websocket.send_json = AsyncMock()
    return websocket


class TestCaseDeviceReadingSend:
    """Device readings send test suite."""

    async def test_device_reading_send(self):
        """Test every websocket gets only the readings of the devices it watches."""
        first, second, idle = build_websocket(), build_websocket(), build_websocket()
        websockets = DeviceWebSockets()
        websockets.subscribe(first, {DEVICE_UUID})
        websockets.subscribe(second, {DEVICE_UUID, SECOND_DEVICE_UUID})
        websockets.subscribe(idle, {UNKNOWN_DEVICE_UUID})
        readings = [
            build_reading(DEVICE_UUID, Decimal('10.5')),
            build_reading(SECOND_DEVICE_UUID, Decimal('12.5')),
            build_reading(DEVICE_UUID, Decimal('11.5')),
        ]
        with patch('api.device.services.device_websockets', websockets):
            await send_readings(readings)
        [first_message] = [call.args[0] for call in first.send_json.await_args_list]
        [second_message] = [call.args[0] for call in second.send_json.await_args_list]
        assert first_message['type'] == 'readings'
        assert [item['value'] for item in first_message['items']] == ['10.5', '11.5']
        assert sorted(item['value'] for item in second_message['items']) == ['10.5', '11.5', '12.5']
        idle.send_json.assert_not_awaited()

    async def test_device_reading_send_closed_websocket(self):
        """Test closed websocket is removed when the readings are sent to it."""
        closed = build_websocket()
        closed.send_json.side_effect = RuntimeError()
        websockets = DeviceWebSockets()
        websockets.subscribe(closed, {DEVICE_UUID})
        with patch('api.device.services.device_websockets', websockets):
            await send_readings([build_reading(DEVICE_UUID)])
        assert closed not in websockets.devices
