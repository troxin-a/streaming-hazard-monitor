import pytest

from api.device.sessions import DeviceSession
from tests.fixtures.reading import UNKNOWN_DEVICE_UUID

pytestmark = pytest.mark.integration


class TestCaseDevicePlaceList:
    """Places of the devices list test suite."""

    async def test_device_place_list(self, override_get_async_session, device, neighbour_device, foreign_device):
        """Test building and company of every requested device are returned in one dictionary."""
        uuids = {device.uuid, neighbour_device.uuid, foreign_device.uuid}
        places = await DeviceSession(override_get_async_session).get_device_places(uuids)
        assert {uuid: (place.building_uuid, place.company_uuid) for uuid, place in places.items()} == {
            item.uuid: (item.building.uuid, item.building.company_uuid)
            for item in (device, neighbour_device, foreign_device)
        }

    async def test_device_place_list_unknown_device(self, override_get_async_session, device):
        """Test device that does not exist is absent from the places."""
        places = await DeviceSession(override_get_async_session).get_device_places({device.uuid, UNKNOWN_DEVICE_UUID})
        assert set(places) == {device.uuid}
