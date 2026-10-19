import pytest

from api.device.sessions import DeviceSession
from tests.fixtures.reading import UNKNOWN_DEVICE_UUID

pytestmark = pytest.mark.integration


class TestCaseDeviceVisibleList:
    """Visible devices among the requested ones test suite."""

    async def test_device_visible_list_employee(
            self, override_get_async_session, user, device, neighbour_device, foreign_device,
    ):
        """Test an employee gets only the devices of their building."""
        uuids = {device.uuid, neighbour_device.uuid, foreign_device.uuid}
        visible = await DeviceSession(override_get_async_session).get_visible_device_uuids(user, uuids)
        assert visible == {device.uuid}

    async def test_device_visible_list_director(
            self, override_get_async_session, director, device, neighbour_device, foreign_device,
    ):
        """Test a director gets the devices of every building of their company."""
        uuids = {device.uuid, neighbour_device.uuid, foreign_device.uuid}
        visible = await DeviceSession(override_get_async_session).get_visible_device_uuids(director, uuids)
        assert visible == {device.uuid, neighbour_device.uuid}

    async def test_device_visible_list_superuser(
            self, override_get_async_session, superuser, device, neighbour_device, foreign_device,
    ):
        """Test a superuser gets the devices of every company."""
        uuids = {device.uuid, neighbour_device.uuid, foreign_device.uuid}
        visible = await DeviceSession(override_get_async_session).get_visible_device_uuids(superuser, uuids)
        assert visible == uuids

    async def test_device_visible_list_unknown_device(self, override_get_async_session, superuser, device):
        """Test device that does not exist is absent from the visible devices."""
        uuids = {device.uuid, UNKNOWN_DEVICE_UUID}
        visible = await DeviceSession(override_get_async_session).get_visible_device_uuids(superuser, uuids)
        assert visible == {device.uuid}
