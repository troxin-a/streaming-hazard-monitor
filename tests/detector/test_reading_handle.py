from decimal import Decimal

import pytest

from detector.services import handle_readings
from shared.config.settings import config
from shared.device.enums import AlertLevel
from tests.fixtures.reading import (
    build_reading_records, build_record, DEVICE_UUID, SECOND_DEVICE_UUID, UNKNOWN_DEVICE_UUID,
)
from tests.fixtures.threshold import build_states

pytestmark = pytest.mark.unit

RISE_COUNT = config.detector.DETECTOR_RISE_COUNT
FALL_COUNT = config.detector.DETECTOR_FALL_COUNT


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
    def test_reading_handle_threshold_bounds(self, value, level):
        """Test reading has the highest level with the threshold below its value."""
        states = build_states()
        handle_readings(build_reading_records(DEVICE_UUID, *[value] * RISE_COUNT), states)
        assert states[DEVICE_UUID].level == level

    def test_reading_handle_alert_start(self):
        """Test series of readings above a threshold of the device without an alert starts the alert of their level."""
        states = build_states()
        [(reading, level)] = handle_readings(build_reading_records(DEVICE_UUID, *['120.5'] * RISE_COUNT), states)
        assert reading.device_uuid == DEVICE_UUID
        assert reading.value == Decimal('120.5')
        assert level == AlertLevel.LEVEL_3
        assert states[DEVICE_UUID].level == AlertLevel.LEVEL_3

    def test_reading_handle_partition(self):
        """Test reading sets the partition of its message in the state of the device."""
        states = build_states()
        handle_readings(build_reading_records(DEVICE_UUID, '3'), states)
        assert states[DEVICE_UUID].partition == 0

    def test_reading_handle_short_rise(self):
        """Test series of readings above the level shorter than the rise count changes nothing."""
        states = build_states()
        assert handle_readings(build_reading_records(DEVICE_UUID, *['120.5'] * (RISE_COUNT - 1)), states) == []
        assert states[DEVICE_UUID].level is None

    def test_reading_handle_rise_over_batches(self):
        """Test series of readings above the level counts over several batches."""
        states = build_states()
        assert handle_readings(build_reading_records(DEVICE_UUID, *['120.5'] * (RISE_COUNT - 1)), states) == []
        [(_, level)] = handle_readings(build_reading_records(DEVICE_UUID, '120.5'), states)
        assert level == AlertLevel.LEVEL_3
        assert states[DEVICE_UUID].level == AlertLevel.LEVEL_3

    def test_reading_handle_rise_interrupted(self):
        """Test reading of the level of the device starts the series of readings above it again."""
        states = build_states()
        values = ['120.5'] * (RISE_COUNT - 1) + ['3'] + ['120.5'] * (RISE_COUNT - 1)
        assert handle_readings(build_reading_records(DEVICE_UUID, *values), states) == []
        assert states[DEVICE_UUID].level is None

    def test_reading_handle_rise_last_level(self):
        """Test series of readings above the level raises it to the level of the last reading of the series."""
        states = build_states()
        values = ['60'] + ['500'] * (RISE_COUNT - 2) + ['120.5']
        handle_readings(build_reading_records(DEVICE_UUID, *values), states)
        assert states[DEVICE_UUID].level == AlertLevel.LEVEL_3

    def test_reading_handle_rise_from_level(self):
        """Test series of readings above the level of the alert in progress raises the level."""
        states = build_states({DEVICE_UUID: AlertLevel.LEVEL_3})
        [(_, level)] = handle_readings(build_reading_records(DEVICE_UUID, *['500'] * RISE_COUNT), states)
        assert level == AlertLevel.LEVEL_4
        assert states[DEVICE_UUID].level == AlertLevel.LEVEL_4

    def test_reading_handle_series_after_change(self):
        """Test series of readings starts again after the level changes."""
        states = build_states()
        values = ['120.5'] * RISE_COUNT + ['500'] * (RISE_COUNT - 1)
        [(_, level)] = handle_readings(build_reading_records(DEVICE_UUID, *values), states)
        assert level == AlertLevel.LEVEL_3
        assert states[DEVICE_UUID].level == AlertLevel.LEVEL_3

    def test_reading_handle_fall(self):
        """Test series of readings below the level of the alert in progress lowers the level."""
        states = build_states({DEVICE_UUID: AlertLevel.LEVEL_3})
        [(_, level)] = handle_readings(build_reading_records(DEVICE_UUID, *['30'] * FALL_COUNT), states)
        assert level == AlertLevel.LEVEL_1
        assert states[DEVICE_UUID].level == AlertLevel.LEVEL_1

    def test_reading_handle_short_fall(self):
        """Test series of readings below the level shorter than the fall count changes nothing."""
        states = build_states({DEVICE_UUID: AlertLevel.LEVEL_3})
        assert handle_readings(build_reading_records(DEVICE_UUID, *['30'] * (FALL_COUNT - 1)), states) == []
        assert states[DEVICE_UUID].level == AlertLevel.LEVEL_3

    def test_reading_handle_fall_interrupted(self):
        """Test reading above the level starts the series of readings below it again."""
        states = build_states({DEVICE_UUID: AlertLevel.LEVEL_3})
        values = ['30'] * (FALL_COUNT - 1) + ['500'] + ['30'] * (FALL_COUNT - 1)
        assert handle_readings(build_reading_records(DEVICE_UUID, *values), states) == []
        assert states[DEVICE_UUID].level == AlertLevel.LEVEL_3

    def test_reading_handle_fall_last_level(self):
        """Test series of readings below the level lowers it to the level of the last reading of the series."""
        states = build_states({DEVICE_UUID: AlertLevel.LEVEL_4})
        values = ['120.5'] + ['3'] * (FALL_COUNT - 2) + ['30']
        handle_readings(build_reading_records(DEVICE_UUID, *values), states)
        assert states[DEVICE_UUID].level == AlertLevel.LEVEL_1

    def test_reading_handle_alert_end(self):
        """Test series of readings below every threshold ends the alert in progress."""
        states = build_states({DEVICE_UUID: AlertLevel.LEVEL_3})
        [(_, level)] = handle_readings(build_reading_records(DEVICE_UUID, *['3'] * FALL_COUNT), states)
        assert level is None
        assert states[DEVICE_UUID].level is None

    def test_reading_handle_unknown_device(self):
        """Test readings of the device without loaded thresholds change nothing."""
        states = build_states()
        assert handle_readings(build_reading_records(UNKNOWN_DEVICE_UUID, *['500'] * RISE_COUNT), states) == []
        assert states == build_states()

    @pytest.mark.parametrize('value', [
        b'not json',
        b'{}',
        b'{"device_uuid": "abc", "value": "1", "received_at": "2026-10-10T12:00:00Z"}',
    ])
    def test_reading_handle_invalid_message(self, value):
        """Test message that does not match the reading scheme changes nothing."""
        states = build_states()
        assert handle_readings([build_record(value)], states) == []
        assert states == build_states()

    def test_reading_handle_several_devices(self):
        """Test level changes of the devices of one batch are returned together in their order."""
        states = build_states({SECOND_DEVICE_UUID: AlertLevel.LEVEL_2})
        batch = (
            build_reading_records(DEVICE_UUID, *['120.5'] * RISE_COUNT)
            + build_reading_records(SECOND_DEVICE_UUID, *['3'] * FALL_COUNT)
        )
        changes = handle_readings(batch, states)
        assert [(reading.device_uuid, level) for reading, level in changes] == [
            (DEVICE_UUID, AlertLevel.LEVEL_3),
            (SECOND_DEVICE_UUID, None),
        ]

    def test_reading_handle_changed_and_unchanged(self):
        """Test only the readings that change the level of their device are returned."""
        states = build_states({SECOND_DEVICE_UUID: AlertLevel.LEVEL_3})
        batch = [
            build_record(b'not json'),
            *build_reading_records(SECOND_DEVICE_UUID, *['120.5'] * RISE_COUNT),
            *build_reading_records(UNKNOWN_DEVICE_UUID, *['500'] * RISE_COUNT),
            *build_reading_records(DEVICE_UUID, *['30'] * RISE_COUNT),
        ]
        [(reading, level)] = handle_readings(batch, states)
        assert (reading.device_uuid, level) == (DEVICE_UUID, AlertLevel.LEVEL_1)

    def test_reading_handle_empty_batch(self):
        """Test batch without messages changes nothing."""
        states = build_states()
        assert handle_readings([], states) == []
        assert states == build_states()
