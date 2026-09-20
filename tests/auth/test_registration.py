import pytest
from starlette import status

from tests.base.base_test import BaseTestCase

pytestmark = pytest.mark.integration


class TestCaseRegistration(BaseTestCase):
    """Registration test suite."""
    url = '/auth/registration/'

    def payload(self, **overrides) -> dict:
        """Build a registration payload."""
        data = {
            'username': 'employee',
            'name': 'Сотрудник',
            'password1': self.password,
            'password2': self.password,
        }
        data.update(overrides)
        return data

    async def test_registration(self, building):
        """Test employee registration."""
        response = await self.make_post(self.url, None, self.payload(building_uuid=f'{building.uuid}'))
        assert response == {'username': 'employee', 'name': 'Сотрудник'}

        registered = await self.make_get('/user/me/', 'employee')
        assert registered['name'] == 'Сотрудник'
        assert registered['is_superuser'] is False

    async def test_registration_without_building(self, building):
        """Test registration requires a building."""
        await self.make_post(self.url, None, self.payload(), status.HTTP_422_UNPROCESSABLE_CONTENT)

    async def test_registration_unknown_building(self, building):
        """Test registration for unknown building."""
        await self.make_post(
            self.url, None, self.payload(building_uuid=self.unknown_uuid), status.HTTP_404_NOT_FOUND,
        )

    async def test_registration_password_mismatch(self, building):
        """Test registration with different passwords."""
        data = self.payload(building_uuid=f'{building.uuid}', password2='another')
        await self.make_post(self.url, None, data, status.HTTP_422_UNPROCESSABLE_CONTENT)

    async def test_registration_duplicate_username(self, building, user):
        """Test registration with an already taken username."""
        data = self.payload(username=user.username, building_uuid=f'{building.uuid}')
        await self.make_post(self.url, None, data, status.HTTP_409_CONFLICT)
