from datetime import datetime, UTC
from decimal import Decimal
from uuid import UUID

from shared.reading.schemes import ReadingMessageScheme

READING_VALUE = Decimal('120.5')
READING_RECEIVED_AT = datetime(2026, 10, 10, 12, 3, tzinfo=UTC)

DEVICE_UUID = UUID('11111111-1111-1111-1111-111111111111')
UNKNOWN_DEVICE_UUID = UUID('22222222-2222-2222-2222-222222222222')


def build_reading(device_uuid: UUID, value: Decimal = READING_VALUE) -> ReadingMessageScheme:
    """Build the reading of the device."""
    return ReadingMessageScheme(device_uuid=device_uuid, value=value, received_at=READING_RECEIVED_AT)


def build_reading_message(device_uuid: UUID, value: str) -> bytes:
    """Build the message of the readings topic with the reading of the device."""
    return build_reading(device_uuid, Decimal(value)).model_dump_json().encode()
