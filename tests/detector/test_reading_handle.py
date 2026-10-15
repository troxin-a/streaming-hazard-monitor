from decimal import Decimal

import pytest

from detector.services import handle_readings
from shared.device.enums import AlertLevel
from tests.fixtures.reading import (
    build_reading_record, build_record, DEVICE_UUID, SECOND_DEVICE_UUID, UNKNOWN_DEVICE_UUID,
)
from tests.fixtures.threshold import build_states

pytestmark = pytest.mark.unit


class TestCaseReadingHandle:
    """Readings handle test suite."""

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
        states = build_states()
        batch = [build_reading_record(DEVICE_UUID, value)]
        await handle_readings(batch, states, detector_session)
        assert states[DEVICE_UUID].level == level

    async def test_reading_handle_alert_start(self, detector_session):
        """Test reading above a threshold of the device without an alert starts the alert of its level."""
        states = build_states()
        batch = [build_reading_record(DEVICE_UUID, '120.5')]
        await handle_readings(batch, states, detector_session)
        detector_session.change_level.assert_awaited_once()
        [(reading, level)] = detector_session.change_level.await_args.args[0]
        assert reading.device_uuid == DEVICE_UUID
        assert reading.value == Decimal('120.5')
        assert level == AlertLevel.LEVEL_3
        assert states == build_states({DEVICE_UUID: AlertLevel.LEVEL_3})

    async def test_reading_handle_same_level(self, detector_session):
        """Test reading of the level of the alert in progress changes nothing."""
        states = build_states({DEVICE_UUID: AlertLevel.LEVEL_3})
        batch = [build_reading_record(DEVICE_UUID, '120.5')]
        await handle_readings(batch, states, detector_session)
        detector_session.change_level.assert_not_awaited()
        assert states == build_states({DEVICE_UUID: AlertLevel.LEVEL_3})

    @pytest.mark.parametrize('value, level', [
        ('30', AlertLevel.LEVEL_1),
        ('500', AlertLevel.LEVEL_4),
    ])
    async def test_reading_handle_other_level(self, detector_session, value, level):
        """Test reading of a lower or a higher level than the alert in progress changes the level."""
        states = build_states({DEVICE_UUID: AlertLevel.LEVEL_3})
        batch = [build_reading_record(DEVICE_UUID, value)]
        await handle_readings(batch, states, detector_session)
        detector_session.change_level.assert_awaited_once()
        [(_, changed_level)] = detector_session.change_level.await_args.args[0]
        assert changed_level == level
        assert states == build_states({DEVICE_UUID: level})

    async def test_reading_handle_alert_end(self, detector_session):
        """Test reading below every threshold ends the alert in progress."""
        states = build_states({DEVICE_UUID: AlertLevel.LEVEL_3})
        batch = [build_reading_record(DEVICE_UUID, '3')]
        await handle_readings(batch, states, detector_session)
        detector_session.change_level.assert_awaited_once()
        [(_, changed_level)] = detector_session.change_level.await_args.args[0]
        assert changed_level is None
        assert states[DEVICE_UUID].level is None

    async def test_reading_handle_normal_value(self, detector_session):
        """Test reading below every threshold of the device without an alert changes nothing."""
        states = build_states()
        batch = [build_reading_record(DEVICE_UUID, '3')]
        await handle_readings(batch, states, detector_session)
        detector_session.change_level.assert_not_awaited()
        assert states == build_states()

    async def test_reading_handle_unknown_device(self, detector_session):
        """Test reading of the device without loaded thresholds changes nothing."""
        states = build_states()
        batch = [build_reading_record(UNKNOWN_DEVICE_UUID, '500')]
        await handle_readings(batch, states, detector_session)
        detector_session.change_level.assert_not_awaited()
        assert states == build_states()

    @pytest.mark.parametrize('value', [
        b'not json',
        b'{}',
        b'{"device_uuid": "abc", "value": "1", "received_at": "2026-10-10T12:00:00Z"}',
    ])
    async def test_reading_handle_invalid_message(self, detector_session, value):
        """Test message that does not match the reading scheme changes nothing."""
        states = build_states()
        await handle_readings([build_record(value)], states, detector_session)
        detector_session.change_level.assert_not_awaited()
        assert states == build_states()

    async def test_reading_handle_several_devices(self, detector_session):
        """Test level changes of the devices of one batch are saved together."""
        states = build_states({SECOND_DEVICE_UUID: AlertLevel.LEVEL_2})
        batch = [build_reading_record(DEVICE_UUID, '120.5'), build_reading_record(SECOND_DEVICE_UUID, '3')]
        await handle_readings(batch, states, detector_session)
        detector_session.change_level.assert_awaited_once()
        changes = detector_session.change_level.await_args.args[0]
        assert [(reading.device_uuid, level) for reading, level in changes] == [
            (DEVICE_UUID, AlertLevel.LEVEL_3),
            (SECOND_DEVICE_UUID, None),
        ]

    async def test_reading_handle_changed_and_unchanged(self, detector_session):
        """Test only the readings that change the level of their device are saved."""
        states = build_states({SECOND_DEVICE_UUID: AlertLevel.LEVEL_3})
        batch = [
            build_record(b'not json'),
            build_reading_record(SECOND_DEVICE_UUID, '120.5'),
            build_reading_record(UNKNOWN_DEVICE_UUID, '500'),
            build_reading_record(DEVICE_UUID, '30'),
        ]
        await handle_readings(batch, states, detector_session)
        [(reading, level)] = detector_session.change_level.await_args.args[0]
        assert (reading.device_uuid, level) == (DEVICE_UUID, AlertLevel.LEVEL_1)

    async def test_reading_handle_empty_batch(self, detector_session):
        """Test batch without messages changes nothing."""
        states = build_states()
        await handle_readings([], states, detector_session)
        detector_session.change_level.assert_not_awaited()
        assert states == build_states()
