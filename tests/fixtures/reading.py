from datetime import datetime, UTC
from decimal import Decimal
from uuid import UUID

from aiokafka import ConsumerRecord

from shared.config.settings import config
from shared.reading.schemes import ReadingMessageScheme

READING_VALUE = Decimal('120.5')
READING_RECEIVED_AT = datetime(2026, 10, 10, 12, 3, tzinfo=UTC)

DEVICE_UUID = UUID('11111111-1111-1111-1111-111111111111')
SECOND_DEVICE_UUID = UUID('33333333-3333-3333-3333-333333333333')
UNKNOWN_DEVICE_UUID = UUID('22222222-2222-2222-2222-222222222222')


def build_reading(device_uuid: UUID, value: Decimal = READING_VALUE) -> ReadingMessageScheme:
    """Build the reading of the device."""
    return ReadingMessageScheme(device_uuid=device_uuid, value=value, received_at=READING_RECEIVED_AT)


def build_record(value: bytes | None) -> ConsumerRecord:
    """Build the record of the readings topic with the value or without a value."""
    return ConsumerRecord(
        topic=config.kafka.KAFKA_TOPIC_SENSOR_READINGS,
        partition=0,
        offset=0,
        timestamp=int(READING_RECEIVED_AT.timestamp() * 1000),
        timestamp_type=0,
        key=None,
        value=value,
        checksum=None,
        serialized_key_size=-1,
        serialized_value_size=-1 if value is None else len(value),
        headers=[],
    )


def build_reading_record(device_uuid: UUID, value: str) -> ConsumerRecord:
    """Build the record of the readings topic with the reading of the device."""
    return build_record(build_reading(device_uuid, Decimal(value)).model_dump_json().encode())


def build_reading_records(device_uuid: UUID, *values: str) -> list[ConsumerRecord]:
    """Build the records of the readings topic with the readings of the device in a row."""
    return [build_reading_record(device_uuid, value) for value in values]
