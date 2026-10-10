from typing import Iterator
from unittest.mock import AsyncMock

import pytest
from aiokafka import AIOKafkaProducer

from receiver.main import app
from receiver.producers import get_producer


@pytest.fixture(scope='function')
def telemetry_producer() -> Iterator[AsyncMock]:
    """Producer of the receiver replaced with a mock that records sent messages."""
    producer = AsyncMock(spec=AIOKafkaProducer)
    app.dependency_overrides[get_producer] = lambda: producer
    yield producer
    del app.dependency_overrides[get_producer]
