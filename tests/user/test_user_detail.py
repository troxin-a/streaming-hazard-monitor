import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.fixtures.building import BUILDING_DATA, COMPANY_DATA

pytestmark = pytest.mark.integration


class TestCaseCurrentUser(BaseTestCase):
    """Current user test suite."""
    url = '/user/me/'

    async def test_current_user(self, user, building):
        """Test current user returns the owner of the token with its building and company."""
        response = await self.make_get(self.url, user.username)
        assert response == {
            'uuid': f'{user.uuid}',
            'name': user.name,
            'is_superuser': False,
            'building': {
                'uuid': f'{building.uuid}',
                'name': BUILDING_DATA['name'],
                'company': {'uuid': f'{building.company_uuid}', 'name': COMPANY_DATA['name']},
            },
        }

    async def test_current_superuser(self, superuser):
        """Test current user without a building reports superuser rights."""
        response = await self.make_get(self.url, superuser.username)
        assert response['is_superuser'] is True
        assert response['building'] is None

    async def test_current_user_401(self, user):
        """Test current user by non-authenticated user."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_current_user_405(self, user):
        """Test current user wrong request method."""
        await self.make_put(self.url, user.username, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


class TestCaseUserDetail(BaseTestCase):
    """User detail test suite."""
    url = '/user/{uuid}/'

    async def test_user_detail(self, user, building):
        """Test user detail by uuid returns the building and its company."""
        response = await self.make_get(self.url.format(uuid=user.uuid), user.username)
        assert response['uuid'] == f'{user.uuid}'
        assert response['is_superuser'] is False
        assert response['building']['name'] == BUILDING_DATA['name']
        assert response['building']['company'] == {
            'uuid': f'{building.company_uuid}', 'name': COMPANY_DATA['name'],
        }

    async def test_user_detail_without_building(self, superuser):
        """Test user detail for a user that belongs to no building."""
        response = await self.make_get(self.url.format(uuid=superuser.uuid), superuser.username)
        assert response == {
            'uuid': f'{superuser.uuid}', 'name': superuser.name, 'is_superuser': True, 'building': None,
        }

    async def test_user_detail_another_building(self, user, neighbour):
        """Test user detail of an employee of another building."""
        await self.make_get(
            self.url.format(uuid=neighbour.uuid), user.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_user_detail_another_building_by_director(self, director, neighbour):
        """Test user detail of an employee of another building of the same company."""
        response = await self.make_get(self.url.format(uuid=neighbour.uuid), director.username)
        assert response['uuid'] == f'{neighbour.uuid}'

    async def test_user_detail_another_company(self, director, other_director):
        """Test user detail of a user of another company."""
        await self.make_get(
            self.url.format(uuid=other_director.uuid), director.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_user_detail_401(self, user):
        """Test user detail by non-authenticated user."""
        await self.make_get(self.url.format(uuid=user.uuid), status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_user_detail_404(self, user):
        """Test user detail for unknown user."""
        await self.make_get(
            self.url.format(uuid=self.unknown_uuid), user.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_user_detail_422(self, user):
        """Test user detail with malformed uuid."""
        await self.make_get(
            self.url.format(uuid='not-a-uuid'), user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
