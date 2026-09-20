import pytest
from starlette import status

from shared.user.enums import UserRole
from tests.base.base_test import BaseTestCase

pytestmark = pytest.mark.integration

NEW_NAME = {'name': 'Новое имя'}
NEW_PASSWORD = 'qwerty123!S'


class TestCaseUserUpdate(BaseTestCase):
    """User update test suite."""
    url = '/user/{uuid}/'

    async def test_user_updates_themselves(self, user):
        """Test an employee changes their own name."""
        response = await self.make_patch(self.url.format(uuid=user.uuid), user.username, NEW_NAME)
        assert response['name'] == NEW_NAME['name']

    async def test_user_updates_own_password(self, user):
        """Test an employee changes their own password."""
        data = {'password1': NEW_PASSWORD, 'password2': NEW_PASSWORD}
        await self.make_patch(self.url.format(uuid=user.uuid), user.username, data)

        self.password = NEW_PASSWORD
        access, _ = await self._login(user.username)
        assert access

    async def test_user_updates_colleague(self, user):
        """Test an employee changes another employee of their building."""
        items = (await self.make_get('/user/?size=50', user.username))['items']
        colleague_uuid = next(item['uuid'] for item in items if item['uuid'] != f'{user.uuid}')
        response = await self.make_patch(
            self.url.format(uuid=colleague_uuid), user.username, NEW_NAME, status.HTTP_403_FORBIDDEN,
        )
        assert response['detail'] == 'Access denied'

    async def test_user_updates_own_building(self, user, second_building):
        """Test an employee changes their own building."""
        data = {'building_uuid': f'{second_building.uuid}'}
        response = await self.make_patch(
            self.url.format(uuid=user.uuid), user.username, data, status.HTTP_403_FORBIDDEN,
        )
        assert response['detail'] == 'Access denied'

    async def test_user_updates_own_role(self, user):
        """Test an employee changes their own role."""
        data = {'role': UserRole.DIRECTOR.value}
        await self.make_patch(self.url.format(uuid=user.uuid), user.username, data, status.HTTP_403_FORBIDDEN)

    async def test_director_updates_employee(self, director, user):
        """Test a director changes an employee of their company."""
        response = await self.make_patch(self.url.format(uuid=user.uuid), director.username, NEW_NAME)
        assert response['name'] == NEW_NAME['name']

    async def test_director_updates_employee_building(self, director, user, second_building):
        """Test a director moves an employee to another building of the company."""
        data = {'building_uuid': f'{second_building.uuid}'}
        response = await self.make_patch(self.url.format(uuid=user.uuid), director.username, data)
        assert response['building_uuid'] == f'{second_building.uuid}'

    async def test_director_updates_colleague_director(self, director, colleague_director):
        """Test a director changes another director of their company."""
        response = await self.make_patch(self.url.format(uuid=colleague_director.uuid), director.username, NEW_NAME)
        assert response['name'] == NEW_NAME['name']

    async def test_director_updates_foreign_building(self, director, user, other_director):
        """Test a director moves an employee to a building of another company."""
        data = {'building_uuid': f'{other_director.building_uuid}'}
        response = await self.make_patch(
            self.url.format(uuid=user.uuid), director.username, data, status.HTTP_404_NOT_FOUND,
        )
        assert response['detail'] == 'Building not found'

    async def test_director_updates_foreign_user(self, director, other_director):
        """Test a director changes a user of another company."""
        response = await self.make_patch(
            self.url.format(uuid=other_director.uuid), director.username, NEW_NAME, status.HTTP_404_NOT_FOUND,
        )
        assert response['detail'] == 'User not found'

    async def test_director_updates_role(self, director, user):
        """Test a director changes the role of an employee."""
        data = {'role': UserRole.DIRECTOR.value}
        await self.make_patch(self.url.format(uuid=user.uuid), director.username, data, status.HTTP_403_FORBIDDEN)

    async def test_director_updates_company(self, director, user, company):
        """Test a director moves an employee to another company."""
        data = {'company_uuid': f'{company.uuid}'}
        await self.make_patch(self.url.format(uuid=user.uuid), director.username, data, status.HTTP_403_FORBIDDEN)

    async def test_superuser_updates_role(self, superuser, user):
        """Test superuser changes the role of an employee."""
        data = {'role': UserRole.DIRECTOR.value}
        response = await self.make_patch(self.url.format(uuid=user.uuid), superuser.username, data)
        assert response['role'] == UserRole.DIRECTOR.value

    async def test_superuser_updates_company_keeping_building(self, superuser, other_director, company):
        """Test superuser moves a user to another company while the building stays in the old one."""
        data = {'company_uuid': f'{company.uuid}'}
        response = await self.make_patch(
            self.url.format(uuid=other_director.uuid), superuser.username, data, status.HTTP_404_NOT_FOUND,
        )
        assert response['detail'] == 'Building not found'

    async def test_user_update_401(self, user):
        """Test user update by non-authenticated user."""
        await self.make_patch(self.url.format(uuid=user.uuid), None, NEW_NAME, status.HTTP_401_UNAUTHORIZED)

    async def test_user_update_404(self, director):
        """Test user update for unknown user."""
        await self.make_patch(
            self.url.format(uuid=self.unknown_uuid), director.username, NEW_NAME, status.HTTP_404_NOT_FOUND,
        )

    async def test_user_update_password_mismatch(self, user):
        """Test user update with different passwords."""
        data = {'password1': NEW_PASSWORD, 'password2': 'another'}
        await self.make_patch(
            self.url.format(uuid=user.uuid), user.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
