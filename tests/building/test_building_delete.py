import pytest
from starlette import status

from tests.base.base_test import BaseTestCase

pytestmark = pytest.mark.integration


class TestCaseBuildingDelete(BaseTestCase):
    """Building delete test suite."""
    url = '/building/{uuid}/'

    async def test_building_delete_by_director(self, director, second_building):
        """Test building without users is deleted by the director of the company."""
        url = self.url.format(uuid=second_building.uuid)
        await self.make_delete(url, director.username)
        await self.make_get(url, director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_delete(self, superuser, building):
        """Test building without users is deleted by superuser."""
        url = self.url.format(uuid=building.uuid)
        await self.make_delete(url, superuser.username)
        await self.make_get(url, superuser.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_delete_foreign_building(self, other_director, building):
        """Test building delete by a director of another company."""
        url = self.url.format(uuid=building.uuid)
        await self.make_delete(url, other_director.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_delete_401(self, building):
        """Test building delete by non-authenticated user."""
        url = self.url.format(uuid=building.uuid)
        await self.make_delete(url, None, status_code=status.HTTP_401_UNAUTHORIZED)

    async def test_building_delete_403(self, user, building):
        """Test building delete by an employee."""
        url = self.url.format(uuid=building.uuid)
        await self.make_delete(url, user.username, status_code=status.HTTP_403_FORBIDDEN)

    async def test_building_delete_404(self, superuser):
        """Test building delete for unknown building."""
        url = self.url.format(uuid=self.unknown_uuid)
        await self.make_delete(url, superuser.username, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_delete_409(self, superuser, user, building):
        """Test building with users is not deleted."""
        url = self.url.format(uuid=building.uuid)
        await self.make_delete(url, superuser.username, status_code=status.HTTP_409_CONFLICT)
