import pytest
from starlette import status

from shared.user.enums import UserRole
from tests.base.base_test import BaseTestCase

pytestmark = pytest.mark.integration


class TestCaseUserCreate(BaseTestCase):
    """User create test suite."""
    url = '/user/'

    def payload(self, **overrides) -> dict:
        """Build a user payload."""
        data = {
            'username': 'employee',
            'name': 'Сотрудник',
            'role': UserRole.EMPLOYEE.value,
            'password1': self.password,
            'password2': self.password,
        }
        data.update(overrides)
        return data

    async def test_director_created_by_superuser(self, superuser, company):
        """Test director create by superuser."""
        data = self.payload(
            username='new_director',
            name='Директор',
            role=UserRole.DIRECTOR.value,
            company_uuid=f'{company.uuid}',
        )
        response = await self.make_post(self.url, superuser.username, data, status.HTTP_201_CREATED)
        assert response['role'] == UserRole.DIRECTOR.value
        assert response['company_uuid'] == f'{company.uuid}'
        assert response['building_uuid'] is None

    async def test_employee_created_by_superuser(self, superuser, building):
        """Test employee create by superuser."""
        data = self.payload(company_uuid=f'{building.company_uuid}', building_uuid=f'{building.uuid}')
        response = await self.make_post(self.url, superuser.username, data, status.HTTP_201_CREATED)
        assert response['role'] == UserRole.EMPLOYEE.value
        assert response['building_uuid'] == f'{building.uuid}'

    async def test_employee_created_by_director(self, director, building):
        """Test employee create by director of the company."""
        data = self.payload(building_uuid=f'{building.uuid}')
        response = await self.make_post(self.url, director.username, data, status.HTTP_201_CREATED)
        assert response['company_uuid'] == f'{building.company_uuid}'
        assert response['building_uuid'] == f'{building.uuid}'

    async def test_employee_create_without_building(self, director):
        """Test employee create requires a building."""
        response = await self.make_post(
            self.url, director.username, self.payload(), status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
        assert response['detail'][0]['field'] == 'building_uuid'

    async def test_created_employee_can_login(self, director, building):
        """Test created employee gets a working password."""
        data = self.payload(building_uuid=f'{building.uuid}')
        await self.make_post(self.url, director.username, data, status.HTTP_201_CREATED)

        access, _ = await self._login(data['username'])
        assert access

    async def test_user_create_401(self, building):
        """Test user create by non-authenticated user."""
        data = self.payload(building_uuid=f'{building.uuid}')
        await self.make_post(self.url, None, data, status.HTTP_401_UNAUTHORIZED)

    async def test_director_create_403_by_director(self, director, company):
        """Test director create by another director."""
        data = self.payload(role=UserRole.DIRECTOR.value, company_uuid=f'{company.uuid}')
        response = await self.make_post(self.url, director.username, data, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_user_create_403_by_employee(self, user, building):
        """Test user create by an employee."""
        data = self.payload(username='another', building_uuid=f'{building.uuid}')
        response = await self.make_post(self.url, user.username, data, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_user_create_foreign_building(self, director, other_director):
        """Test employee create in a building of another company."""
        data = self.payload(building_uuid=f'{other_director.building_uuid}')
        response = await self.make_post(self.url, director.username, data, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Building not found'

    async def test_user_create_unknown_company(self, superuser):
        """Test user create in unknown company."""
        data = self.payload(role=UserRole.DIRECTOR.value, company_uuid=self.unknown_uuid)
        response = await self.make_post(self.url, superuser.username, data, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Company not found'

    async def test_user_create_without_company_by_superuser(self, superuser, building):
        """Test user create by superuser without a company."""
        data = self.payload(building_uuid=f'{building.uuid}')
        response = await self.make_post(self.url, superuser.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)
        assert response['detail'][0]['field'] == 'company_uuid'

    async def test_user_create_password_mismatch(self, director, building):
        """Test user create with different passwords."""
        data = self.payload(building_uuid=f'{building.uuid}', password2='another')
        await self.make_post(self.url, director.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)

    async def test_user_create_duplicate_username(self, director, building, user):
        """Test user create with an already taken username."""
        data = self.payload(username=user.username, building_uuid=f'{building.uuid}')
        await self.make_post(self.url, director.username, data, status.HTTP_409_CONFLICT)

    async def test_user_create_unknown_role(self, director, building):
        """Test user create with an unknown role."""
        data = self.payload(role='ceo', building_uuid=f'{building.uuid}')
        await self.make_post(self.url, director.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)
