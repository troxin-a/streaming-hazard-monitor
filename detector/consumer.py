from uuid import UUID

from aiokafka import AIOKafkaConsumer, ConsumerRebalanceListener, TopicPartition

from detector.devices_state import DeviceState
from detector.services import reload_states
from shared.config.settings import config


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


def create_consumer() -> AIOKafkaConsumer:
    """Create consumer of the threshold detector."""
    return AIOKafkaConsumer(
        bootstrap_servers=config.kafka.KAFKA_HOST,
        group_id=config.kafka.KAFKA_GROUP_THRESHOLD_DETECTOR,
        enable_auto_commit=False,
        auto_offset_reset='earliest',
    )
