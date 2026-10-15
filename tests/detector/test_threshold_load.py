import pytest

from detector.devices_state import DeviceState
from detector.sessions import DetectorSession
from tests.fixtures.threshold import DEFAULT_VALUES, DEVICE_VALUES

pytestmark = pytest.mark.integration


class TestCaseThresholdLoad:
    """Threshold detector thresholds load test suite."""

    async def test_threshold_load_device(self, override_get_async_session, device, device_thresholds):
        """Test thresholds set for the device are loaded for it."""
        states = await DetectorSession(override_get_async_session).get_states()
        assert states == {device.uuid: DeviceState(thresholds=DEVICE_VALUES)}

    async def test_threshold_load_default(self, override_get_async_session, device, default_thresholds):
        """Test default thresholds of the device type are loaded for the device without its own ones."""
        states = await DetectorSession(override_get_async_session).get_states()
        assert states == {device.uuid: DeviceState(thresholds=DEFAULT_VALUES)}

    async def test_threshold_load_device_over_default(
            self, override_get_async_session, device, device_with_api_key, default_thresholds, device_thresholds,
    ):
        """Test thresholds set for the device are loaded instead of the default ones of its type."""
        states = await DetectorSession(override_get_async_session).get_states()
        assert states == {
            device.uuid: DeviceState(thresholds=DEVICE_VALUES),
            device_with_api_key.uuid: DeviceState(thresholds=DEFAULT_VALUES),
        }

    async def test_threshold_load_default_shared(
            self, override_get_async_session, device, device_with_api_key, default_thresholds,
    ):
        """Test devices of one type without their own thresholds share one object of the default ones."""
        states = await DetectorSession(override_get_async_session).get_states()
        assert states[device.uuid].thresholds is states[device_with_api_key.uuid].thresholds

    async def test_threshold_load_other_type(self, override_get_async_session, device, methane_default_thresholds):
        """Test default thresholds of another device type are not loaded for the device."""
        states = await DetectorSession(override_get_async_session).get_states()
        assert states == {}
