import pytest

from detector.sessions import DetectorSession
from tests.fixtures.alert import ALERT_LEVEL

pytestmark = pytest.mark.integration


class TestCaseLevelLoad:
    """Threshold detector alert levels load test suite."""

    async def test_level_load(self, override_get_async_session, device, alert):
        """Test level of the alert in progress is loaded for its device."""
        levels = await DetectorSession(override_get_async_session).get_levels()
        assert levels == {device.uuid: ALERT_LEVEL}

    async def test_level_load_ended_alert(self, override_get_async_session, device, ended_alert):
        """Test level of the ended alert is not loaded."""
        levels = await DetectorSession(override_get_async_session).get_levels()
        assert levels == {}

    async def test_level_load_without_alerts(self, override_get_async_session, device):
        """Test device without alerts has no loaded level."""
        levels = await DetectorSession(override_get_async_session).get_levels()
        assert levels == {}
