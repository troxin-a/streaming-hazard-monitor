import pytest
from starlette import status

from shared.device.enums import DeviceType
from tests.base.base_test import BaseTestCase
from tests.conftest import get_url_size
from tests.fixtures.alert import ALERT_LEVEL, ALERT_STARTED_AT
from tests.fixtures.building import BUILDING_DATA

pytestmark = pytest.mark.integration


class TestCaseAlertList(BaseTestCase):
    """Alert list test suite."""
    url = '/alert/'

    async def test_alert_list(self, user, device, alert):
        """Test an employee sees the alert in progress of their building with its device and building."""
        response = await self.make_get(self.url, user.username)
        assert response['items'] == [{
            'uuid': f'{alert.uuid}',
            'level': ALERT_LEVEL.value,
            'started_at': ALERT_STARTED_AT.isoformat().replace('+00:00', 'Z'),
            'device': {'uuid': f'{device.uuid}', 'name': device.name, 'type': DeviceType.CO.value},
            'building': {'uuid': f'{alert.building_uuid}', 'name': BUILDING_DATA['name']},
        }]

    async def test_alert_list_another_building(self, user, alert, neighbour_alert):
        """Test an employee does not see the alerts of another building of their company."""
        response = await self.make_get(self.url, user.username)
        assert [item['uuid'] for item in response['items']] == [f'{alert.uuid}']

    async def test_alert_list_without_building(self, user_without_building, alert):
        """Test an employee without a building sees no alerts."""
        response = await self.make_get(self.url, user_without_building.username)
        assert response['total'] == 0

    async def test_alert_list_own_company(self, director, alert, neighbour_alert, foreign_alert):
        """Test a director sees the alerts of every building of their company."""
        response = await self.make_get(self.url, director.username)
        assert [item['uuid'] for item in response['items']] == [f'{neighbour_alert.uuid}', f'{alert.uuid}']

    async def test_alert_list_superuser(self, superuser, alert, neighbour_alert, foreign_alert):
        """Test superuser sees every alert, the most dangerous and then the latest first."""
        response = await self.make_get(self.url, superuser.username)
        uuids = [item['uuid'] for item in response['items']]
        assert uuids == [f'{neighbour_alert.uuid}', f'{foreign_alert.uuid}', f'{alert.uuid}']

    async def test_alert_list_ended(self, superuser, ended_alert):
        """Test ended alert is not listed."""
        response = await self.make_get(self.url, superuser.username)
        assert response['total'] == 0

    @pytest.mark.parametrize('size, page, count', [(2, 1, 2), (2, 2, 1)])
    async def test_alert_list_pagination(self, superuser, alert, neighbour_alert, foreign_alert, size, page, count):
        """Test alert list respects page size."""
        url = get_url_size(self.url, size, page)
        response = await self.make_get(url, superuser.username)
        assert response['total'] == 3
        assert len(response['items']) == count

    async def test_alert_list_401(self, alert):
        """Test alert list by non-authenticated user."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_alert_list_422(self, user):
        """Test alert list negative size."""
        url = get_url_size(self.url, -1)
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
