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
        url = self.url.format(uuid=user.uuid)
        response = await self.make_patch(url, user.username, NEW_NAME)
        assert response['name'] == NEW_NAME['name']

    async def test_user_updates_own_password(self, user):
        """Test an employee changes their own password."""
        url = self.url.format(uuid=user.uuid)
        data = {'password1': NEW_PASSWORD, 'password2': NEW_PASSWORD}
        await self.make_patch(url, user.username, data)

        self.password = NEW_PASSWORD
        access, _ = await self._login(user.username)
        assert access

    async def test_user_updates_colleague(self, user, many_users):
        """Test an employee changes another employee of their building."""
        url = self.url.format(uuid=many_users[0].uuid)
        response = await self.make_patch(url, user.username, NEW_NAME, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_user_updates_own_building(self, user, second_building):
        """Test an employee changes their own building."""
        url = self.url.format(uuid=user.uuid)
        data = {'building_uuid': f'{second_building.uuid}'}
        response = await self.make_patch(url, user.username, data, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_user_updates_own_role(self, user):
        """Test an employee changes their own role."""
        url = self.url.format(uuid=user.uuid)
        data = {'role': UserRole.DIRECTOR.value}
        await self.make_patch(url, user.username, data, status.HTTP_403_FORBIDDEN)

    async def test_director_updates_employee(self, director, user):
        """Test a director changes an employee of their company."""
        url = self.url.format(uuid=user.uuid)
        response = await self.make_patch(url, director.username, NEW_NAME)
        assert response['name'] == NEW_NAME['name']

    async def test_director_updates_employee_building(self, director, user, second_building):
        """Test a director moves an employee to another building of the company."""
        url = self.url.format(uuid=user.uuid)
        data = {'building_uuid': f'{second_building.uuid}'}
        response = await self.make_patch(url, director.username, data)
        assert response['building_uuid'] == f'{second_building.uuid}'

    async def test_director_updates_colleague_director(self, director, colleague_director):
        """Test a director changes another director of their company."""
        url = self.url.format(uuid=colleague_director.uuid)
        response = await self.make_patch(url, director.username, NEW_NAME)
        assert response['name'] == NEW_NAME['name']

    async def test_director_updates_foreign_building(self, director, user, other_building):
        """Test a director moves an employee to a building of another company."""
        url = self.url.format(uuid=user.uuid)
        data = {'building_uuid': f'{other_building.uuid}'}
        response = await self.make_patch(url, director.username, data, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Building not found'

    async def test_director_updates_foreign_user(self, director, other_director):
        """Test a director changes a user of another company."""
        url = self.url.format(uuid=other_director.uuid)
        response = await self.make_patch(url, director.username, NEW_NAME, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'User not found'

    async def test_director_updates_role(self, director, user):
        """Test a director changes the role of an employee."""
        url = self.url.format(uuid=user.uuid)
        data = {'role': UserRole.DIRECTOR.value}
        await self.make_patch(url, director.username, data, status.HTTP_403_FORBIDDEN)

    async def test_director_updates_company(self, director, user, other_company):
        """Test a director moves an employee to another company."""
        url = self.url.format(uuid=user.uuid)
        data = {'company_uuid': f'{other_company.uuid}'}
        await self.make_patch(url, director.username, data, status.HTTP_403_FORBIDDEN)

    async def test_superuser_updates_role(self, superuser, user):
        """Test superuser changes the role of an employee."""
        url = self.url.format(uuid=user.uuid)
        data = {'role': UserRole.DIRECTOR.value}
        response = await self.make_patch(url, superuser.username, data)
        assert response['role'] == UserRole.DIRECTOR.value

    async def test_superuser_updates_company_keeping_building(self, superuser, other_director, company):
        """Test superuser moves a user to another company while the building stays in the old one."""
        url = self.url.format(uuid=other_director.uuid)
        data = {'company_uuid': f'{company.uuid}'}
        response = await self.make_patch(url, superuser.username, data, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Building not found'

    async def test_superuser_updates_company_without_building(self, superuser, other_director, company):
        """Test superuser moves a user to another company leaving them without a building."""
        url = self.url.format(uuid=other_director.uuid)
        data = {'company_uuid': f'{company.uuid}', 'building_uuid': None}
        response = await self.make_patch(url, superuser.username, data)
        assert response['company_uuid'] == f'{company.uuid}'
        assert response['building_uuid'] is None

    async def test_user_update_401(self, user):
        """Test user update by non-authenticated user."""
        url = self.url.format(uuid=user.uuid)
        await self.make_patch(url, None, NEW_NAME, status.HTTP_401_UNAUTHORIZED)

    async def test_user_update_404(self, director):
        """Test user update for unknown user."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_patch(url, director.username, NEW_NAME, status.HTTP_404_NOT_FOUND)

    async def test_user_update_password_mismatch(self, user):
        """Test user update with different passwords."""
        url = self.url.format(uuid=user.uuid)
        data = {'password1': NEW_PASSWORD, 'password2': 'another'}
        await self.make_patch(url, user.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)
