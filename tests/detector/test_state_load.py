import pytest

from detector.devices_state import DeviceState
from detector.sessions import DetectorSession
from tests.fixtures.alert import ALERT_LEVEL
from tests.fixtures.threshold import DEFAULT_VALUES

pytestmark = pytest.mark.integration


class TestCaseStateLoad:
    """Threshold detector device states load test suite."""

    async def test_state_load_level(self, override_get_async_session, device, default_thresholds, alert):
        """Test level of the alert in progress is loaded into the state of its device."""
        states = await DetectorSession(override_get_async_session).get_states()
        assert states == {device.uuid: DeviceState(thresholds=DEFAULT_VALUES, level=ALERT_LEVEL)}

    async def test_state_load_ended_alert(self, override_get_async_session, device, default_thresholds, ended_alert):
        """Test level of the ended alert is not loaded into the state of its device."""
        states = await DetectorSession(override_get_async_session).get_states()
        assert states == {device.uuid: DeviceState(thresholds=DEFAULT_VALUES)}

    async def test_state_load_level_without_thresholds(self, override_get_async_session, device, alert):
        """Test device with the alert in progress and without thresholds has no state."""
        states = await DetectorSession(override_get_async_session).get_states()
        assert states == {}
