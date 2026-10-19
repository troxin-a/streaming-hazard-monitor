import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from aiokafka import ConsumerRecord, TopicPartition

from api.device.consumer import consume_readings_to_websockets, READINGS_SEND_SECONDS
from api.device.websocket import DeviceWebSockets
from shared.config.settings import config
from tests.fixtures.reading import build_record, build_reading_record, DEVICE_UUID, SECOND_DEVICE_UUID

pytestmark = pytest.mark.unit

PARTITION = TopicPartition(config.kafka.KAFKA_TOPIC_SENSOR_READINGS, 0)


def build_consumer(*batches: list[ConsumerRecord]) -> MagicMock:
    """Build the consumer of the readings topic that returns the batches of records and then stops the task."""
    consumer = MagicMock()
    consumer.start = AsyncMock()
    consumer.stop = AsyncMock()
    results = [{PARTITION: records} for records in batches]
    consumer.getmany = AsyncMock(side_effect=[*results, asyncio.CancelledError])
    return consumer


def build_websockets(*watched: UUID) -> DeviceWebSockets:
    """Build the websockets with one websocket watching the devices or without websockets when none is given."""
    websockets = DeviceWebSockets()
    if watched:
        websocket = MagicMock()
        websockets.add(websocket, MagicMock())
        websockets.subscribe(websocket, set(watched))
    return websockets


class TestCaseDeviceReadingRead:
    """Device readings read test suite."""

    async def test_device_reading_consume(self):
        """Test readings fetched in a second are sent to the websockets together and invalid messages are skipped."""
        consumer = build_consumer([
            build_reading_record(DEVICE_UUID, '10.5'),
            build_record(b'not json'),
            build_reading_record(SECOND_DEVICE_UUID, '11.5'),
        ])
        sleep, send = AsyncMock(), AsyncMock()
        with patch('api.device.consumer.create_consumer', return_value=consumer), \
                patch('api.device.consumer.device_websockets', build_websockets(DEVICE_UUID)), \
                patch('api.device.consumer.broadcast_readings', send), \
                patch('api.device.consumer.asyncio.sleep', sleep):
            with pytest.raises(asyncio.CancelledError):
                await consume_readings_to_websockets()
        [readings] = [call.args[0] for call in send.await_args_list]
        assert [(reading.device_uuid, reading.value) for reading in readings] == [
            (DEVICE_UUID, Decimal('10.5')),
            (SECOND_DEVICE_UUID, Decimal('11.5')),
        ]
        sleep.assert_awaited_with(READINGS_SEND_SECONDS)
        consumer.stop.assert_awaited_once()

    async def test_device_reading_consume_every_second(self):
        """Test readings fetched in different seconds are sent separately."""
        consumer = build_consumer(
            [build_reading_record(DEVICE_UUID, '10.5')],
            [build_reading_record(DEVICE_UUID, '11.5')],
        )
        send = AsyncMock()
        with patch('api.device.consumer.create_consumer', return_value=consumer), \
                patch('api.device.consumer.device_websockets', build_websockets(DEVICE_UUID)), \
                patch('api.device.consumer.broadcast_readings', send), \
                patch('api.device.consumer.asyncio.sleep', AsyncMock()):
            with pytest.raises(asyncio.CancelledError):
                await consume_readings_to_websockets()
        assert [[reading.value for reading in call.args[0]] for call in send.await_args_list] == [
            [Decimal('10.5')],
            [Decimal('11.5')],
        ]

    async def test_device_reading_consume_without_subscriptions(self):
        """Test readings are not sent when no websocket watches devices."""
        consumer = build_consumer([build_reading_record(DEVICE_UUID, '10.5')])
        send = AsyncMock()
        with patch('api.device.consumer.create_consumer', return_value=consumer), \
                patch('api.device.consumer.device_websockets', build_websockets()), \
                patch('api.device.consumer.broadcast_readings', send), \
                patch('api.device.consumer.asyncio.sleep', AsyncMock()):
            with pytest.raises(asyncio.CancelledError):
                await consume_readings_to_websockets()
        send.assert_not_awaited()
