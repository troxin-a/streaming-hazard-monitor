import pytest

from detector.sessions import DetectorSession
from tests.fixtures.threshold import DEFAULT_VALUES, DEVICE_VALUES

pytestmark = pytest.mark.integration


class TestCaseThresholdLoad:
    """Threshold detector thresholds load test suite."""

    async def test_threshold_load_device(self, override_get_async_session, device, device_thresholds):
        """Test thresholds set for the device are loaded for it."""
        thresholds = await DetectorSession(override_get_async_session).get_thresholds()
        assert thresholds == {device.uuid: DEVICE_VALUES}

    async def test_threshold_load_default(self, override_get_async_session, device, default_thresholds):
        """Test default thresholds of the device type are loaded for the device without its own ones."""
        thresholds = await DetectorSession(override_get_async_session).get_thresholds()
        assert thresholds == {device.uuid: DEFAULT_VALUES}

    async def test_threshold_load_device_over_default(
            self, override_get_async_session, device, device_with_api_key, default_thresholds, device_thresholds,
    ):
        """Test thresholds set for the device are loaded instead of the default ones of its type."""
        thresholds = await DetectorSession(override_get_async_session).get_thresholds()
        assert thresholds == {device.uuid: DEVICE_VALUES, device_with_api_key.uuid: DEFAULT_VALUES}

    async def test_threshold_load_other_type(self, override_get_async_session, device, methane_default_thresholds):
        """Test default thresholds of another device type are not loaded for the device."""
        thresholds = await DetectorSession(override_get_async_session).get_thresholds()
        assert thresholds == {}
