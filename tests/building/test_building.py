import pytest
from starlette import status

from tests.base.base_test import BaseTestCase
from tests.conftest import get_url_size
from tests.fixtures.building import BUILDING_DATA, COMPANY_DATA

pytestmark = pytest.mark.integration

NEW_BUILDING = {'name': 'Офис'}


class TestCaseBuildingList(BaseTestCase):
    """Building list test suite."""
    url = '/building/'

    async def test_building_list(self, user, building, other_director):
        """Test an employee sees only the buildings of their company."""
        response = await self.make_get(self.url, user.username)
        assert response['total'] == 1
        assert response['items'][0]['uuid'] == f'{building.uuid}'
        assert response['items'][0]['company']['name'] == COMPANY_DATA['name']

    async def test_building_list_own_building(self, user, second_building, other_director):
        """Test an employee sees only their own building."""
        response = await self.make_get(self.url, user.username)
        assert response['total'] == 1
        assert response['items'][0]['uuid'] == f'{user.building_uuid}'

    async def test_building_list_without_building(self, user_without_building, building):
        """Test an employee without a building sees no buildings."""
        response = await self.make_get(self.url, user_without_building.username)
        assert response['total'] == 0

    async def test_building_list_own_company(self, director, second_building, other_director):
        """Test a director sees every building of their company."""
        response = await self.make_get(self.url, director.username)
        assert response['total'] == 2

    async def test_building_list_superuser(self, superuser, building, other_director):
        """Test superuser sees every building."""
        response = await self.make_get(self.url, superuser.username)
        assert response['total'] == 2

    async def test_building_list_pagination(self, superuser, building, other_director):
        """Test building list respects page size."""
        url = get_url_size(self.url, 1)
        response = await self.make_get(url, superuser.username)
        assert response['total'] == 2
        assert len(response['items']) == 1

    async def test_building_list_401(self, user):
        """Test building list by non-authenticated user."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_building_list_422(self, user):
        """Test building list negative size."""
        url = get_url_size(self.url, -1)
        await self.make_get(url, user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


class TestCaseBuildingDetail(BaseTestCase):
    """Building detail test suite."""
    url = '/building/{uuid}/'

    async def test_building_detail(self, user, building):
        """Test building detail returns its company."""
        response = await self.make_get(self.url.format(uuid=building.uuid), user.username)
        assert response['uuid'] == f'{building.uuid}'
        assert response['name'] == BUILDING_DATA['name']
        assert response['company'] == {'uuid': f'{building.company_uuid}', 'name': COMPANY_DATA['name']}

    async def test_building_detail_another_building(self, user, second_building):
        """Test building detail of another building of the same company."""
        await self.make_get(
            self.url.format(uuid=second_building.uuid), user.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_building_detail_another_building_by_director(self, director, second_building):
        """Test building detail of another building of the same company by its director."""
        response = await self.make_get(self.url.format(uuid=second_building.uuid), director.username)
        assert response['uuid'] == f'{second_building.uuid}'

    async def test_building_detail_foreign_company(self, user, other_director):
        """Test building detail of another company."""
        await self.make_get(
            self.url.format(uuid=other_director.building_uuid),
            user.username,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_building_detail_401(self, building):
        """Test building detail by non-authenticated user."""
        await self.make_get(self.url.format(uuid=building.uuid), status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_building_detail_404(self, user):
        """Test building detail for unknown building."""
        await self.make_get(
            self.url.format(uuid=self.unknown_uuid), user.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_building_detail_422(self, user):
        """Test building detail with malformed uuid."""
        await self.make_get(
            self.url.format(uuid='not-a-uuid'), user.username, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )


class TestCaseBuildingCreate(BaseTestCase):
    """Building create test suite."""
    url = '/building/'

    async def test_building_create_by_director(self, director, building):
        """Test building create by the director of the company."""
        data = {**NEW_BUILDING, 'company_uuid': f'{building.company_uuid}'}
        response = await self.make_post(self.url, director.username, data, status.HTTP_201_CREATED)
        assert response['name'] == NEW_BUILDING['name']
        assert response['company']['uuid'] == f'{building.company_uuid}'

    async def test_building_create(self, superuser, company):
        """Test building create by superuser."""
        data = {**NEW_BUILDING, 'company_uuid': f'{company.uuid}'}
        response = await self.make_post(self.url, superuser.username, data, status.HTTP_201_CREATED)
        assert response['name'] == NEW_BUILDING['name']
        assert response['company'] == {'uuid': f'{company.uuid}', 'name': COMPANY_DATA['name']}

    async def test_building_create_foreign_company(self, director, company):
        """Test building create in another company."""
        data = {**NEW_BUILDING, 'company_uuid': f'{company.uuid}'}
        response = await self.make_post(self.url, director.username, data, status.HTTP_404_NOT_FOUND)
        assert response['detail'] == 'Company not found'

    async def test_building_create_401(self, company):
        """Test building create by non-authenticated user."""
        data = {**NEW_BUILDING, 'company_uuid': f'{company.uuid}'}
        await self.make_post(self.url, None, data, status.HTTP_401_UNAUTHORIZED)

    async def test_building_create_403(self, user, building):
        """Test building create by an employee."""
        data = {**NEW_BUILDING, 'company_uuid': f'{building.company_uuid}'}
        response = await self.make_post(self.url, user.username, data, status.HTTP_403_FORBIDDEN)
        assert response['detail'] == 'Access denied'

    async def test_building_create_404(self, superuser):
        """Test building create for unknown company."""
        data = {**NEW_BUILDING, 'company_uuid': self.unknown_uuid}
        await self.make_post(self.url, superuser.username, data, status.HTTP_404_NOT_FOUND)

    async def test_building_create_422(self, superuser):
        """Test building create without company."""
        await self.make_post(self.url, superuser.username, NEW_BUILDING, status.HTTP_422_UNPROCESSABLE_CONTENT)


class TestCaseBuildingUpdate(BaseTestCase):
    """Building update test suite."""
    url = '/building/{uuid}/'

    async def test_building_update_by_director(self, director, building):
        """Test building update by the director of the company."""
        response = await self.make_patch(self.url.format(uuid=building.uuid), director.username, NEW_BUILDING)
        assert response['name'] == NEW_BUILDING['name']
        assert response['company']['uuid'] == f'{building.company_uuid}'

    async def test_building_update(self, superuser, building):
        """Test building update by superuser."""
        response = await self.make_patch(self.url.format(uuid=building.uuid), superuser.username, NEW_BUILDING)
        assert response['name'] == NEW_BUILDING['name']
        assert response['company']['uuid'] == f'{building.company_uuid}'

    async def test_building_update_company(self, superuser, building, company):
        """Test building is moved to another company by superuser."""
        data = {'company_uuid': f'{company.uuid}'}
        response = await self.make_patch(self.url.format(uuid=building.uuid), superuser.username, data)
        assert response['company']['uuid'] == f'{company.uuid}'

    async def test_building_update_foreign_company(self, director, building, company):
        """Test building is not moved to another company by a director."""
        data = {'company_uuid': f'{company.uuid}'}
        response = await self.make_patch(
            self.url.format(uuid=building.uuid), director.username, data, status.HTTP_404_NOT_FOUND,
        )
        assert response['detail'] == 'Company not found'

    async def test_building_update_foreign_building(self, other_director, building):
        """Test building update by a director of another company."""
        await self.make_patch(
            self.url.format(uuid=building.uuid), other_director.username, NEW_BUILDING, status.HTTP_404_NOT_FOUND,
        )

    async def test_building_update_401(self, building):
        """Test building update by non-authenticated user."""
        await self.make_patch(
            self.url.format(uuid=building.uuid), None, NEW_BUILDING, status.HTTP_401_UNAUTHORIZED,
        )

    async def test_building_update_403(self, user, building):
        """Test building update by an employee of that company."""
        response = await self.make_patch(
            self.url.format(uuid=building.uuid), user.username, NEW_BUILDING, status.HTTP_403_FORBIDDEN,
        )
        assert response['detail'] == 'Access denied'

    async def test_building_update_404(self, superuser):
        """Test building update for unknown building."""
        await self.make_patch(
            self.url.format(uuid=self.unknown_uuid), superuser.username, NEW_BUILDING, status.HTTP_404_NOT_FOUND,
        )


class TestCaseBuildingDelete(BaseTestCase):
    """Building delete test suite."""
    url = '/building/{uuid}/'

    async def test_building_delete_by_director(self, director, building):
        """Test building without users is deleted by the director of the company."""
        data = {**NEW_BUILDING, 'company_uuid': f'{building.company_uuid}'}
        created = await self.make_post('/building/', director.username, data, status.HTTP_201_CREATED)

        await self.make_delete(self.url.format(uuid=created['uuid']), director.username)
        await self.make_get(
            self.url.format(uuid=created['uuid']), director.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_building_delete(self, superuser, company):
        """Test building without users is deleted by superuser."""
        data = {**NEW_BUILDING, 'company_uuid': f'{company.uuid}'}
        created = await self.make_post('/building/', superuser.username, data, status.HTTP_201_CREATED)

        await self.make_delete(self.url.format(uuid=created['uuid']), superuser.username)
        await self.make_get(
            self.url.format(uuid=created['uuid']), superuser.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_building_delete_foreign_building(self, other_director, building):
        """Test building delete by a director of another company."""
        await self.make_delete(
            self.url.format(uuid=building.uuid), other_director.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_building_delete_401(self, building):
        """Test building delete by non-authenticated user."""
        await self.make_delete(
            self.url.format(uuid=building.uuid), None, status_code=status.HTTP_401_UNAUTHORIZED,
        )

    async def test_building_delete_403(self, user, building):
        """Test building delete by an employee."""
        await self.make_delete(
            self.url.format(uuid=building.uuid), user.username, status_code=status.HTTP_403_FORBIDDEN,
        )

    async def test_building_delete_404(self, superuser):
        """Test building delete for unknown building."""
        await self.make_delete(
            self.url.format(uuid=self.unknown_uuid), superuser.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_building_delete_409(self, superuser, user):
        """Test building with users is not deleted."""
        await self.make_delete(
            self.url.format(uuid=user.building_uuid), superuser.username, status_code=status.HTTP_409_CONFLICT,
        )
