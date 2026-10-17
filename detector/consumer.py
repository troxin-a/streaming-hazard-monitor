from uuid import UUID

from aiokafka import AIOKafkaConsumer, ConsumerRebalanceListener, TopicPartition
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from detector.devices_state import DeviceState
from detector.sessions import DetectorSession
from shared.config.settings import config


class ConsumerRebalancer(ConsumerRebalanceListener):
    """Consumer rebalance listener."""

    def __init__(self, states: dict[UUID, DeviceState], session_maker: async_sessionmaker[AsyncSession]) -> None:
        self.states = states
        self.session_maker = session_maker
        self.owned: frozenset[TopicPartition] = frozenset()

    async def on_partitions_revoked(self, revoked: frozenset[TopicPartition]) -> None:
        """Before balancing."""
        self.owned = revoked

    async def on_partitions_assigned(self, assigned: set[TopicPartition]) -> None:
        """After balancing."""
        kept_partitions = self.owned.intersection(assigned)
        kept = {tp.partition for tp in kept_partitions}
        async with self.session_maker() as session:
            new_states = await DetectorSession(session).get_states()
        for device_uuid, new_state in new_states.items():
            old_state = self.states.get(device_uuid)
            if old_state is not None and old_state.partition in kept:
                new_state.level = old_state.level
                new_state.series_count = old_state.series_count
                new_state.partition = old_state.partition
        self.states.clear()
        self.states.update(new_states)


def create_consumer() -> AIOKafkaConsumer:
    """Create consumer of the threshold detector."""
    return AIOKafkaConsumer(
        bootstrap_servers=config.kafka.KAFKA_HOST,
        group_id=config.kafka.KAFKA_GROUP_THRESHOLD_DETECTOR,
        enable_auto_commit=False,
        auto_offset_reset='earliest',
    )
