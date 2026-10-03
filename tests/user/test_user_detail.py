import pytest
from starlette import status

from shared.user.enums import UserRole
from tests.base.base_test import BaseTestCase
from tests.fixtures.building import BUILDING_DATA
from tests.fixtures.company import COMPANY_DATA

pytestmark = pytest.mark.integration


class TestCaseUserDetail(BaseTestCase):
    """User detail test suite."""
    url = '/user/{uuid}/'

    async def test_user_detail(self, user, company):
        """Test user detail by uuid returns the building and its company."""
        url = self.url.format(uuid=user.uuid)
        response = await self.make_get(url, user.username)
        assert response['uuid'] == f'{user.uuid}'
        assert response['is_superuser'] is False
        assert response['building']['name'] == BUILDING_DATA['name']
        assert response['building']['company'] == {'uuid': f'{company.uuid}', 'name': COMPANY_DATA['name']}

    async def test_user_detail_without_building(self, superuser):
        """Test user detail for a user that belongs to no building."""
        url = self.url.format(uuid=superuser.uuid)
        response = await self.make_get(url, superuser.username)
        assert response == {
            'uuid': f'{superuser.uuid}',
            'name': superuser.name,
            'is_superuser': True,
            'role': UserRole.EMPLOYEE,
            'building': None,
        }

    async def test_user_detail_another_building(self, user, neighbour):
        """Test user detail of an employee of another building."""
        url = self.url.format(uuid=neighbour.uuid)
        await self.make_get(url, user.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_user_detail_another_building_by_director(self, director, neighbour):
        """Test user detail of an employee of another building of the same company."""
        url = self.url.format(uuid=neighbour.uuid)
        response = await self.make_get(url, director.username)
        assert response['uuid'] == f'{neighbour.uuid}'

    async def test_user_detail_another_company(self, director, other_director):
        """Test user detail of a user of another company."""
        url = self.url.format(uuid=other_director.uuid)
        await self.make_get(url, director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_user_detail_401(self, user):
        """Test user detail by non-authenticated user."""
        url = self.url.format(uuid=user.uuid)
        await self.make_get(url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_user_detail_404(self, user):
        """Test user detail for unknown user."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_get(url, user.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_user_detail_422(self, user):
        """Test user detail with malformed uuid."""
        url = self.url.format(uuid='not-a-uuid')
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
