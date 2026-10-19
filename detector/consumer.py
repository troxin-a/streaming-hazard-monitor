import logging
from uuid import UUID

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRebalanceListener, TopicPartition
from aiokafka.errors import CommitFailedError
from sqlalchemy.ext.asyncio import AsyncSession

from detector.devices_state import DeviceState
from detector.services import handle_readings, publish_and_save_level_changes, reload_states
from detector.sessions import DetectorSession

logger = logging.getLogger(__name__)


class ConsumerRebalancer(ConsumerRebalanceListener):
    """Consumer rebalance listener."""

    def __init__(self, states: dict[UUID, DeviceState]) -> None:
        self.states = states
        self.owned: frozenset[TopicPartition] = frozenset()

    async def on_partitions_revoked(self, revoked: frozenset[TopicPartition]) -> None:
        """Before balancing."""
        self.owned = revoked

    async def on_partitions_assigned(self, assigned: set[TopicPartition]) -> None:
        """After balancing."""
        kept_partitions = self.owned.intersection(assigned)
        kept = {tp.partition for tp in kept_partitions}
        await reload_states(self.states, kept)


async def consume_readings(
        consumer: AIOKafkaConsumer,
        producer: AIOKafkaProducer,
        states: dict[UUID, DeviceState],
        session: AsyncSession,
) -> None:
    """Read the readings in batches, save the level changes of every partition and commit its offset."""
    detector_session = DetectorSession(session)
    while True:
        batch = await consumer.getmany(timeout_ms=1000, max_records=100)
        for tp, messages in batch.items():
            if messages:
                changes = handle_readings(messages, states)
                await publish_and_save_level_changes(changes, producer, detector_session)
                try:
                    await consumer.commit({tp: messages[-1].offset + 1})
                except CommitFailedError:
                    logger.warning(f'Offset of partition {tp} is not committed: the group has rebalanced')
