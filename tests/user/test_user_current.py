import pytest
from starlette import status

from shared.user.enums import UserRole
from tests.base.base_test import BaseTestCase
from tests.fixtures.building import BUILDING_DATA
from tests.fixtures.company import COMPANY_DATA

pytestmark = pytest.mark.integration


class TestCaseCurrentUser(BaseTestCase):
    """Current user test suite."""
    url = '/user/me/'

    async def test_current_user(self, user, building, company):
        """Test current user returns the owner of the token with its building and company."""
        response = await self.make_get(self.url, user.username)
        assert response == {
            'uuid': f'{user.uuid}',
            'username': user.username,
            'name': user.name,
            'is_superuser': False,
            'role': UserRole.EMPLOYEE,
            'company': {'uuid': f'{company.uuid}', 'name': COMPANY_DATA['name']},
            'building': {
                'uuid': f'{building.uuid}',
                'name': BUILDING_DATA['name'],
                'company': {'uuid': f'{company.uuid}', 'name': COMPANY_DATA['name']},
            },
        }

    async def test_current_director(self, director):
        """Test current user reports the director role."""
        response = await self.make_get(self.url, director.username)
        assert response['role'] == UserRole.DIRECTOR

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
