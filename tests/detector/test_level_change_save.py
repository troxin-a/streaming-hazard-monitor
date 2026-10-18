import pytest
from aiokafka.errors import KafkaError

from detector.services import save_level_changes
from shared.device.enums import AlertLevel
from tests.fixtures.reading import build_reading, DEVICE_UUID

pytestmark = pytest.mark.unit


class TestCaseLevelChangeSave:
    """Threshold detector level change save test suite."""

    async def test_level_change_save_order(self, alert_producer, detector_session):
        """Test level changes are sent to the device levels topic before they are saved as alerts."""
        order = []
        alert_producer.send_and_wait.side_effect = lambda *args: order.append('topic')
        detector_session.change_level.side_effect = lambda *args: order.append('database')
        changes = [(build_reading(DEVICE_UUID), AlertLevel.LEVEL_3)]
        await save_level_changes(changes, alert_producer, detector_session)
        assert order == ['topic', 'database']
        detector_session.change_level.assert_awaited_once_with(changes)

    async def test_level_change_save_not_sent(self, alert_producer, detector_session):
        """Test level changes that are not sent to the device levels topic are not saved."""
        alert_producer.send_and_wait.side_effect = KafkaError()
        with pytest.raises(KafkaError):
            await save_level_changes([(build_reading(DEVICE_UUID), None)], alert_producer, detector_session)
        detector_session.change_level.assert_not_awaited()

    async def test_level_change_save_nothing(self, alert_producer, detector_session):
        """Test batch without level changes sends and saves nothing."""
        await save_level_changes([], alert_producer, detector_session)
        alert_producer.send_and_wait.assert_not_awaited()
        detector_session.change_level.assert_not_awaited()
