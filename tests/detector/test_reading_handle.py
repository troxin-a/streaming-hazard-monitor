import json
from decimal import Decimal
from uuid import UUID

import pytest

from detector.services import detect_level, handle_reading
from shared.device.enums import AlertLevel
from tests.fixtures.threshold import DEFAULT_VALUES

pytestmark = pytest.mark.unit

DEVICE_UUID = UUID('11111111-1111-1111-1111-111111111111')
UNKNOWN_DEVICE_UUID = UUID('22222222-2222-2222-2222-222222222222')
THRESHOLDS = {DEVICE_UUID: DEFAULT_VALUES}


def reading_message(device_uuid: UUID, value: str) -> bytes:
    """Build the message of the readings topic."""
    return json.dumps({
        'device_uuid': str(device_uuid),
        'value': value,
        'received_at': '2026-10-10T12:00:00Z',
    }).encode()


class TestCaseReadingHandle:
    """Reading handle test suite."""

    @pytest.mark.parametrize('value, level', [
        ('-5', None),
        ('20', None),
        ('20.001', AlertLevel.LEVEL_1),
        ('50', AlertLevel.LEVEL_1),
        ('50.001', AlertLevel.LEVEL_2),
        ('100.001', AlertLevel.LEVEL_3),
        ('300', AlertLevel.LEVEL_3),
        ('300.001', AlertLevel.LEVEL_4),
    ])
    def test_detect_level(self, value, level):
        """Test the highest level with the threshold below the value is detected."""
        assert detect_level(Decimal(value), DEFAULT_VALUES) == level

    def test_reading_handle(self):
        """Test alert level is detected by the thresholds of the device of the reading."""
        message = reading_message(DEVICE_UUID, '120.5')
        assert handle_reading(message, THRESHOLDS) == AlertLevel.LEVEL_3

    def test_reading_handle_normal_value(self):
        """Test reading below every threshold has no alert level."""
        message = reading_message(DEVICE_UUID, '3')
        assert handle_reading(message, THRESHOLDS) is None

    def test_reading_handle_unknown_device(self):
        """Test reading of the device without loaded thresholds has no alert level."""
        message = reading_message(UNKNOWN_DEVICE_UUID, '500')
        assert handle_reading(message, THRESHOLDS) is None

    @pytest.mark.parametrize('message', [
        b'not json',
        b'{}',
        b'{"device_uuid": "abc", "value": "1", "received_at": "2026-10-10T12:00:00Z"}',
    ])
    def test_reading_handle_invalid_message(self, message):
        """Test message that does not match the reading scheme has no alert level."""
        assert handle_reading(message, THRESHOLDS) is None
