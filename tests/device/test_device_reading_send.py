from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from api.device.services import broadcast_readings
from api.device.websocket import DeviceWebSockets
from tests.fixtures.reading import build_reading, DEVICE_UUID, SECOND_DEVICE_UUID, UNKNOWN_DEVICE_UUID

pytestmark = pytest.mark.unit


def build_websocket() -> MagicMock:
    """Build the open websocket."""
    websocket = MagicMock()
    websocket.send_json = AsyncMock()
    return websocket


def build_websockets(watched: dict[MagicMock, set[UUID]]) -> DeviceWebSockets:
    """Build the websockets subscribed to the devices."""
    websockets = DeviceWebSockets()
    for websocket, devices in watched.items():
        websockets.add(websocket, MagicMock())
        websockets.subscribe(websocket, devices)
    return websockets


class TestCaseDeviceReadingSend:
    """Device readings send test suite."""

    async def test_device_reading_send(self):
        """Test every websocket gets only the readings of the devices it watches."""
        first, second, idle = build_websocket(), build_websocket(), build_websocket()
        websockets = build_websockets({
            first: {DEVICE_UUID},
            second: {DEVICE_UUID, SECOND_DEVICE_UUID},
            idle: {UNKNOWN_DEVICE_UUID},
        })
        readings = [
            build_reading(DEVICE_UUID, Decimal('10.5')),
            build_reading(SECOND_DEVICE_UUID, Decimal('12.5')),
            build_reading(DEVICE_UUID, Decimal('11.5')),
        ]
        with patch('api.device.services.device_websockets', websockets):
            await broadcast_readings(readings)
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
        websockets = build_websockets({closed: {DEVICE_UUID}})
        with patch('api.device.services.device_websockets', websockets):
            await broadcast_readings([build_reading(DEVICE_UUID)])
        assert closed not in websockets.websockets
