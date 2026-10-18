import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiokafka import TopicPartition
from aiokafka.errors import KafkaConnectionError

from api.device.consumer import consume_level_changes
from shared.config.settings import config
from shared.device.enums import AlertLevel
from tests.fixtures.reading import build_record, DEVICE_UUID, READING_RECEIVED_AT

pytestmark = pytest.mark.unit

LEVEL_CHANGE = json.dumps({
    'device_uuid': str(DEVICE_UUID),
    'level': AlertLevel.LEVEL_3.value,
    'changed_at': READING_RECEIVED_AT.isoformat(),
}).encode()
PARTITION = TopicPartition(config.kafka.KAFKA_TOPIC_DEVICE_LEVELS, 0)


def build_consumer(*batches: list[bytes]) -> MagicMock:
    """Build the consumer of the device levels topic that returns the batches of messages and then stops the task."""
    consumer = MagicMock()
    consumer.start = AsyncMock()
    consumer.stop = AsyncMock()
    results = [{PARTITION: [build_record(value) for value in batch]} for batch in batches]
    consumer.getmany = AsyncMock(side_effect=[*results, asyncio.CancelledError])
    return consumer


class TestCaseDeviceLevelRead:
    """Device level changes read test suite."""

    async def test_device_level_consume(self):
        """Test level changes of a batch are sent to the websockets together and invalid messages are skipped."""
        consumer = build_consumer([], [b'not json', LEVEL_CHANGE, LEVEL_CHANGE])
        send = AsyncMock()
        with patch('api.device.consumer.create_consumer', return_value=consumer), \
                patch('api.device.consumer.send_level_changes', send):
            with pytest.raises(asyncio.CancelledError):
                await consume_level_changes()
        [changes] = [call.args[0] for call in send.await_args_list]
        assert [(change.device_uuid, change.level) for change in changes] == [(DEVICE_UUID, AlertLevel.LEVEL_3)] * 2
        consumer.stop.assert_awaited_once()

    async def test_device_level_consume_kafka_unavailable(self):
        """Test reading the topic starts again after Kafka was unavailable."""
        unavailable = build_consumer()
        unavailable.start.side_effect = KafkaConnectionError()
        available = build_consumer([LEVEL_CHANGE])
        sleep = AsyncMock(side_effect=[None, asyncio.CancelledError])
        with patch('api.device.consumer.create_consumer', side_effect=[unavailable, available]), \
                patch('api.device.consumer.asyncio.sleep', sleep):
            with pytest.raises(asyncio.CancelledError):
                await consume_level_changes()
        unavailable.stop.assert_awaited_once()
        available.start.assert_awaited_once()
