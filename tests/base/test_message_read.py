import json

import pytest

from shared.alert.schemes import LevelChangeMessageScheme
from shared.base.kafka import read_message
from shared.device.enums import AlertLevel
from shared.reading.schemes import ReadingMessageScheme
from tests.fixtures.reading import build_record, DEVICE_UUID, READING_RECEIVED_AT, READING_VALUE

pytestmark = pytest.mark.unit


class TestCaseMessageRead:
    """Kafka message read test suite."""

    def test_message_read(self):
        """Test message is read by the scheme."""
        value = json.dumps({
            'device_uuid': str(DEVICE_UUID),
            'level': AlertLevel.LEVEL_3.value,
            'changed_at': READING_RECEIVED_AT.isoformat(),
        })
        change = read_message(build_record(value.encode()), LevelChangeMessageScheme)
        assert (change.device_uuid, change.level, change.changed_at) == (
            DEVICE_UUID, AlertLevel.LEVEL_3, READING_RECEIVED_AT,
        )

    def test_message_read_other_scheme(self):
        """Test message is read by the scheme it is passed with."""
        value = json.dumps({
            'device_uuid': str(DEVICE_UUID),
            'value': str(READING_VALUE),
            'received_at': READING_RECEIVED_AT.isoformat(),
        })
        reading = read_message(build_record(value.encode()), ReadingMessageScheme)
        assert (reading.device_uuid, reading.value) == (DEVICE_UUID, READING_VALUE)

    @pytest.mark.parametrize('value', [
        b'not json',
        b'{}',
        b'{"device_uuid": "abc", "level": null, "changed_at": "2026-10-10T12:00:00Z"}',
        b'{"device_uuid": "11111111-1111-1111-1111-111111111111", "level": "level_9", "changed_at": "2026-10-10"}',
    ])
    def test_message_read_invalid(self, value):
        """Test message that does not match the scheme is skipped."""
        assert read_message(build_record(value), LevelChangeMessageScheme) is None

    def test_message_read_without_value(self):
        """Test message without a value is skipped."""
        assert read_message(build_record(None), LevelChangeMessageScheme) is None
