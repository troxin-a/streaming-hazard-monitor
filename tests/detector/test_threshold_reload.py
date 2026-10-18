import pytest

from detector.devices_state import DeviceState
from detector.services import reload_states
from shared.device.enums import AlertLevel
from tests.fixtures.alert import ALERT_LEVEL
from tests.fixtures.reading import UNKNOWN_DEVICE_UUID
from tests.fixtures.threshold import DEFAULT_VALUES, DEVICE_VALUES

pytestmark = pytest.mark.integration


class TestCaseThresholdReload:
    """Threshold detector thresholds reload test suite."""

    async def test_threshold_reload_changed(self, device, device_thresholds):
        """Test device of the kept partition takes the thresholds from the database and keeps its level and series."""
        state = DeviceState(thresholds=DEFAULT_VALUES, level=AlertLevel.LEVEL_4, series_count=3, partition=1)
        states = {device.uuid: state}
        await reload_states(states, {1})
        assert states == {
            device.uuid: DeviceState(thresholds=DEVICE_VALUES, level=AlertLevel.LEVEL_4, series_count=3, partition=1),
        }

    async def test_threshold_reload_other_partition(self, device, default_thresholds, alert):
        """Test device of the partition not kept takes its level from the database and no series."""
        state = DeviceState(thresholds=DEFAULT_VALUES, level=AlertLevel.LEVEL_4, series_count=3, partition=2)
        states = {device.uuid: state}
        await reload_states(states, {1})
        assert states == {device.uuid: DeviceState(thresholds=DEFAULT_VALUES, level=ALERT_LEVEL)}

    async def test_threshold_reload_new_device(self, device, default_thresholds, alert):
        """Test device missing from the states takes its thresholds and level from the database."""
        states: dict = {}
        await reload_states(states, {1})
        assert states == {device.uuid: DeviceState(thresholds=DEFAULT_VALUES, level=ALERT_LEVEL)}

    async def test_threshold_reload_removed_device(self):
        """Test device missing from the database is removed from the states."""
        states = {UNKNOWN_DEVICE_UUID: DeviceState(thresholds=DEFAULT_VALUES)}
        await reload_states(states, {1})
        assert states == {}
