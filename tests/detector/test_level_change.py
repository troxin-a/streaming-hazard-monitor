import pytest

from detector.sessions import DetectorSession
from shared.device.enums import AlertLevel
from tests.fixtures.alert import ALERT_LEVEL, ALERT_STARTED_AT, ALERT_VALUE, get_alerts
from tests.fixtures.reading import build_reading, READING_RECEIVED_AT, READING_VALUE, UNKNOWN_DEVICE_UUID

pytestmark = pytest.mark.integration


class TestCaseLevelChange:
    """Threshold detector alert level change test suite."""

    async def test_level_change_start(self, override_get_async_session, device, building):
        """Test alert of the level starts in the building of the device at the time of the reading with its value."""
        session = DetectorSession(override_get_async_session)
        await session.change_level([(build_reading(device.uuid), AlertLevel.LEVEL_3)])
        assert await session.get_levels() == {device.uuid: AlertLevel.LEVEL_3}
        assert await get_alerts(override_get_async_session) == [
            (building.uuid, AlertLevel.LEVEL_3, READING_VALUE, READING_RECEIVED_AT, None),
        ]

    async def test_level_change_end(self, override_get_async_session, device, building, alert):
        """Test alert in progress ends at the time of the reading when the device has no level."""
        session = DetectorSession(override_get_async_session)
        await session.change_level([(build_reading(device.uuid), None)])
        assert await session.get_levels() == {}
        assert await get_alerts(override_get_async_session) == [
            (building.uuid, ALERT_LEVEL, ALERT_VALUE, ALERT_STARTED_AT, READING_RECEIVED_AT),
        ]

    async def test_level_change_other_level(self, override_get_async_session, device, building, alert):
        """Test alert in progress ends and the alert of the other level starts."""
        session = DetectorSession(override_get_async_session)
        await session.change_level([(build_reading(device.uuid), AlertLevel.LEVEL_4)])
        assert await session.get_levels() == {device.uuid: AlertLevel.LEVEL_4}
        assert await get_alerts(override_get_async_session) == [
            (building.uuid, ALERT_LEVEL, ALERT_VALUE, ALERT_STARTED_AT, READING_RECEIVED_AT),
            (building.uuid, AlertLevel.LEVEL_4, READING_VALUE, READING_RECEIVED_AT, None),
        ]

    async def test_level_change_other_building(self, override_get_async_session, neighbour_device, second_building):
        """Test alert of the device of another building starts in that building."""
        session = DetectorSession(override_get_async_session)
        await session.change_level([(build_reading(neighbour_device.uuid), AlertLevel.LEVEL_3)])
        (alert,) = await get_alerts(override_get_async_session)
        assert alert.building_uuid == second_building.uuid

    async def test_level_change_unknown_device(self, override_get_async_session, device):
        """Test alert does not start for the device that does not exist."""
        session = DetectorSession(override_get_async_session)
        await session.change_level([(build_reading(UNKNOWN_DEVICE_UUID), AlertLevel.LEVEL_3)])
        assert await session.get_levels() == {}
        assert await get_alerts(override_get_async_session) == []

    async def test_level_change_ended_alert(self, override_get_async_session, device, ended_alert):
        """Test ended alert keeps the time it ended when another alert starts."""
        session = DetectorSession(override_get_async_session)
        await session.change_level([(build_reading(device.uuid), AlertLevel.LEVEL_1)])
        ended, started = await get_alerts(override_get_async_session)
        assert ended.ended_at == ended_alert.ended_at
        assert started.ended_at is None

    async def test_level_change_other_device(self, override_get_async_session, device, device_with_api_key, alert):
        """Test alert in progress of another device does not end."""
        session = DetectorSession(override_get_async_session)
        await session.change_level([(build_reading(device_with_api_key.uuid), AlertLevel.LEVEL_1)])
        assert await session.get_levels() == {device.uuid: ALERT_LEVEL, device_with_api_key.uuid: AlertLevel.LEVEL_1}

    async def test_level_change_several_devices(
            self, override_get_async_session, device, device_with_api_key, neighbour_device, alert,
    ):
        """Test level changes of several devices are saved together."""
        session = DetectorSession(override_get_async_session)
        changes = [
            (build_reading(device.uuid), None),
            (build_reading(device_with_api_key.uuid), AlertLevel.LEVEL_1),
            (build_reading(neighbour_device.uuid), AlertLevel.LEVEL_4),
        ]
        await session.change_level(changes)
        assert await session.get_levels() == {
            device_with_api_key.uuid: AlertLevel.LEVEL_1,
            neighbour_device.uuid: AlertLevel.LEVEL_4,
        }

    async def test_level_change_known_and_unknown_devices(self, override_get_async_session, device, building):
        """Test alert of the existing device starts when another device of the changes does not exist."""
        session = DetectorSession(override_get_async_session)
        changes = [
            (build_reading(UNKNOWN_DEVICE_UUID), AlertLevel.LEVEL_3),
            (build_reading(device.uuid), AlertLevel.LEVEL_2),
        ]
        await session.change_level(changes)
        assert await get_alerts(override_get_async_session) == [
            (building.uuid, AlertLevel.LEVEL_2, READING_VALUE, READING_RECEIVED_AT, None),
        ]
