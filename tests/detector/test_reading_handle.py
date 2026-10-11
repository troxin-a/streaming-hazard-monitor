from decimal import Decimal

import pytest

from detector.services import handle_reading
from shared.device.enums import AlertLevel
from tests.fixtures.reading import build_reading_message, DEVICE_UUID, UNKNOWN_DEVICE_UUID
from tests.fixtures.threshold import LOADED_THRESHOLDS

pytestmark = pytest.mark.unit


class TestCaseReadingHandle:
    """Reading handle test suite."""

    @pytest.mark.parametrize('value, level', [
        ('-5', None),
        ('20', None),
        ('20.001', AlertLevel.LEVEL_1),
        ('50', AlertLevel.LEVEL_1),
        ('50.001', AlertLevel.LEVEL_2),
        ('100', AlertLevel.LEVEL_2),
        ('100.001', AlertLevel.LEVEL_3),
        ('300', AlertLevel.LEVEL_3),
        ('300.001', AlertLevel.LEVEL_4),
    ])
    async def test_reading_handle_threshold_bounds(self, detector_session, value, level):
        """Test reading has the highest level with the threshold below its value."""
        levels = {}
        message = build_reading_message(DEVICE_UUID, value)
        await handle_reading(message, LOADED_THRESHOLDS, levels, detector_session)
        assert levels.get(DEVICE_UUID) == level

    async def test_reading_handle_alert_start(self, detector_session):
        """Test reading above a threshold of the device without an alert starts the alert of its level."""
        levels = {}
        message = build_reading_message(DEVICE_UUID, '120.5')
        await handle_reading(message, LOADED_THRESHOLDS, levels, detector_session)
        detector_session.change_level.assert_awaited_once()
        reading, level = detector_session.change_level.await_args.args
        assert reading.device_uuid == DEVICE_UUID
        assert reading.value == Decimal('120.5')
        assert level == AlertLevel.LEVEL_3
        assert levels == {DEVICE_UUID: AlertLevel.LEVEL_3}

    async def test_reading_handle_same_level(self, detector_session):
        """Test reading of the level of the alert in progress changes nothing."""
        levels = {DEVICE_UUID: AlertLevel.LEVEL_3}
        message = build_reading_message(DEVICE_UUID, '120.5')
        await handle_reading(message, LOADED_THRESHOLDS, levels, detector_session)
        detector_session.change_level.assert_not_awaited()
        assert levels == {DEVICE_UUID: AlertLevel.LEVEL_3}

    @pytest.mark.parametrize('value, level', [
        ('30', AlertLevel.LEVEL_1),
        ('500', AlertLevel.LEVEL_4),
    ])
    async def test_reading_handle_other_level(self, detector_session, value, level):
        """Test reading of a lower or a higher level than the alert in progress changes the level."""
        levels = {DEVICE_UUID: AlertLevel.LEVEL_3}
        message = build_reading_message(DEVICE_UUID, value)
        await handle_reading(message, LOADED_THRESHOLDS, levels, detector_session)
        detector_session.change_level.assert_awaited_once()
        assert detector_session.change_level.await_args.args[1] == level
        assert levels == {DEVICE_UUID: level}

    async def test_reading_handle_alert_end(self, detector_session):
        """Test reading below every threshold ends the alert in progress."""
        levels = {DEVICE_UUID: AlertLevel.LEVEL_3}
        message = build_reading_message(DEVICE_UUID, '3')
        await handle_reading(message, LOADED_THRESHOLDS, levels, detector_session)
        detector_session.change_level.assert_awaited_once()
        assert detector_session.change_level.await_args.args[1] is None
        assert levels == {}

    async def test_reading_handle_normal_value(self, detector_session):
        """Test reading below every threshold of the device without an alert changes nothing."""
        levels = {}
        message = build_reading_message(DEVICE_UUID, '3')
        await handle_reading(message, LOADED_THRESHOLDS, levels, detector_session)
        detector_session.change_level.assert_not_awaited()
        assert levels == {}

    async def test_reading_handle_unknown_device(self, detector_session):
        """Test reading of the device without loaded thresholds changes nothing."""
        levels = {}
        message = build_reading_message(UNKNOWN_DEVICE_UUID, '500')
        await handle_reading(message, LOADED_THRESHOLDS, levels, detector_session)
        detector_session.change_level.assert_not_awaited()
        assert levels == {}

    @pytest.mark.parametrize('message', [
        b'not json',
        b'{}',
        b'{"device_uuid": "abc", "value": "1", "received_at": "2026-10-10T12:00:00Z"}',
    ])
    async def test_reading_handle_invalid_message(self, detector_session, message):
        """Test message that does not match the reading scheme changes nothing."""
        levels = {}
        await handle_reading(message, LOADED_THRESHOLDS, levels, detector_session)
        detector_session.change_level.assert_not_awaited()
        assert levels == {}
