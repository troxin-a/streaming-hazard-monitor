import pytest
from aiokafka import TopicPartition

from detector.consumer import ConsumerRebalancer
from detector.devices_state import DeviceState
from shared.config.settings import config
from shared.device.enums import AlertLevel
from tests.fixtures.alert import ALERT_LEVEL
from tests.fixtures.reading import UNKNOWN_DEVICE_UUID
from tests.fixtures.threshold import DEFAULT_VALUES

pytestmark = pytest.mark.integration

FIRST_PARTITION = TopicPartition(config.kafka.KAFKA_TOPIC_SENSOR_READINGS, 0)
SECOND_PARTITION = TopicPartition(config.kafka.KAFKA_TOPIC_SENSOR_READINGS, 1)


class TestCasePartitionsAssign:
    """Threshold detector partitions assign test suite."""

    async def test_partitions_assign_reload(self, session_maker, device, default_thresholds, alert):
        """Test states of the devices are replaced with the ones from the database in the same dictionary."""
        states = {UNKNOWN_DEVICE_UUID: DeviceState(thresholds=DEFAULT_VALUES)}
        rebalancer = ConsumerRebalancer(states, session_maker)
        await rebalancer.on_partitions_revoked(frozenset())
        await rebalancer.on_partitions_assigned({FIRST_PARTITION})
        assert states == {device.uuid: DeviceState(thresholds=DEFAULT_VALUES, level=ALERT_LEVEL)}

    async def test_partitions_assign_kept_partition(self, session_maker, device, default_thresholds, alert):
        """Test device of the partition kept by the consumer keeps its level and series of readings."""
        state = DeviceState(thresholds=DEFAULT_VALUES, level=AlertLevel.LEVEL_4, series_count=4, partition=0)
        states = {device.uuid: state}
        rebalancer = ConsumerRebalancer(states, session_maker)
        await rebalancer.on_partitions_revoked(frozenset({FIRST_PARTITION}))
        await rebalancer.on_partitions_assigned({FIRST_PARTITION, SECOND_PARTITION})
        assert states == {device.uuid: state}

    async def test_partitions_assign_returned_partition(self, session_maker, device, default_thresholds, alert):
        """Test device of the partition returned to the consumer takes its level from the database and no series."""
        state = DeviceState(thresholds=DEFAULT_VALUES, level=AlertLevel.LEVEL_4, series_count=3, partition=1)
        states = {device.uuid: state}
        rebalancer = ConsumerRebalancer(states, session_maker)
        await rebalancer.on_partitions_revoked(frozenset({FIRST_PARTITION}))
        await rebalancer.on_partitions_assigned({FIRST_PARTITION, SECOND_PARTITION})
        assert states == {device.uuid: DeviceState(thresholds=DEFAULT_VALUES, level=ALERT_LEVEL)}

    async def test_partitions_assign_first(self, session_maker, device, default_thresholds, alert):
        """Test devices take their states from the database at the first assignment of the consumer."""
        state = DeviceState(thresholds=DEFAULT_VALUES, level=AlertLevel.LEVEL_4, series_count=4, partition=0)
        states = {device.uuid: state}
        rebalancer = ConsumerRebalancer(states, session_maker)
        await rebalancer.on_partitions_revoked(frozenset())
        await rebalancer.on_partitions_assigned({FIRST_PARTITION})
        assert states == {device.uuid: DeviceState(thresholds=DEFAULT_VALUES, level=ALERT_LEVEL)}

    async def test_partitions_assign_during_transaction(
            self, override_get_async_session, session_maker, device, default_thresholds, alert,
    ):
        """Test states are reloaded while the session of the readings handling is in a transaction."""
        states: dict = {}
        rebalancer = ConsumerRebalancer(states, session_maker)
        async with override_get_async_session.begin():
            await rebalancer.on_partitions_revoked(frozenset())
            await rebalancer.on_partitions_assigned({FIRST_PARTITION})
        assert states == {device.uuid: DeviceState(thresholds=DEFAULT_VALUES, level=ALERT_LEVEL)}
