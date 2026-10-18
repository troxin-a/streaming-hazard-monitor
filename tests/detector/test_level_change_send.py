import json

import pytest

from detector.producer import send_level_changes
from shared.config.settings import config
from shared.device.enums import AlertLevel
from tests.fixtures.reading import build_reading, DEVICE_UUID, READING_RECEIVED_AT, SECOND_DEVICE_UUID

pytestmark = pytest.mark.unit


class TestCaseLevelChangeSend:
    """Threshold detector level change send test suite."""

    async def test_level_change_send(self, alert_producer):
        """Test level change is sent to the device levels topic with the device uuid as the key."""
        await send_level_changes(alert_producer, [(build_reading(DEVICE_UUID), AlertLevel.LEVEL_3)])
        alert_producer.send_and_wait.assert_awaited_once()
        topic, value, key = alert_producer.send_and_wait.await_args.args
        assert topic == config.kafka.KAFKA_TOPIC_DEVICE_LEVELS
        assert key == str(DEVICE_UUID).encode()
        assert json.loads(value) == {
            'device_uuid': str(DEVICE_UUID),
            'level': AlertLevel.LEVEL_3.value,
            'changed_at': READING_RECEIVED_AT.isoformat().replace('+00:00', 'Z'),
        }

    async def test_level_change_send_normal(self, alert_producer):
        """Test return of the device to normal is sent without a level."""
        await send_level_changes(alert_producer, [(build_reading(DEVICE_UUID), None)])
        topic, value, key = alert_producer.send_and_wait.await_args.args
        assert json.loads(value)['level'] is None

    async def test_level_change_send_order(self, alert_producer):
        """Test level changes of several devices are sent in their order."""
        changes = [(build_reading(SECOND_DEVICE_UUID), AlertLevel.LEVEL_1), (build_reading(DEVICE_UUID), None)]
        await send_level_changes(alert_producer, changes)
        keys = [call.args[2] for call in alert_producer.send_and_wait.await_args_list]
        assert keys == [str(SECOND_DEVICE_UUID).encode(), str(DEVICE_UUID).encode()]

    async def test_level_change_send_nothing(self, alert_producer):
        """Test batch without level changes sends nothing."""
        await send_level_changes(alert_producer, [])
        alert_producer.send_and_wait.assert_not_awaited()
