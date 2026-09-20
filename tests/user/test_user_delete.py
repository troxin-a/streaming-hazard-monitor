import pytest
from starlette import status

from tests.base.base_test import BaseTestCase

pytestmark = pytest.mark.integration


class TestCaseUserDelete(BaseTestCase):
    """User delete test suite."""
    url = '/user/{uuid}/'

    async def test_director_deletes_employee(self, director, user):
        """Test a director deletes an employee of their company."""
        await self.make_delete(self.url.format(uuid=user.uuid), director.username)
        await self.make_get(
            self.url.format(uuid=user.uuid), director.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_director_deletes_colleague_director(self, director, colleague_director):
        """Test a director deletes another director of their company."""
        await self.make_delete(self.url.format(uuid=colleague_director.uuid), director.username)

    async def test_director_deletes_themselves(self, director):
        """Test a director deletes their own account."""
        await self.make_delete(
            self.url.format(uuid=director.uuid), director.username, status_code=status.HTTP_403_FORBIDDEN,
        )
        still_there = await self.make_get(self.url.format(uuid=director.uuid), director.username)
        assert still_there['uuid'] == f'{director.uuid}'

    async def test_director_deletes_foreign_user(self, director, other_director):
        """Test a director deletes a user of another company."""
        await self.make_delete(
            self.url.format(uuid=other_director.uuid), director.username, status_code=status.HTTP_404_NOT_FOUND,
        )

    async def test_superuser_deletes_user(self, superuser, user):
        """Test superuser deletes any user."""
        await self.make_delete(self.url.format(uuid=user.uuid), superuser.username)

    async def test_superuser_deletes_themselves(self, superuser):
        """Test superuser deletes their own account."""
        await self.make_delete(
            self.url.format(uuid=superuser.uuid), superuser.username, status_code=status.HTTP_403_FORBIDDEN,
        )
        still_there = await self.make_get(self.url.format(uuid=superuser.uuid), superuser.username)
        assert still_there['uuid'] == f'{superuser.uuid}'

    async def test_user_delete_403(self, user, director, neighbour):
        """Test user delete by an employee."""
        await self.make_delete(
            self.url.format(uuid=neighbour.uuid), user.username, status_code=status.HTTP_403_FORBIDDEN,
        )
        still_there = await self.make_get(self.url.format(uuid=neighbour.uuid), director.username)
        assert still_there['uuid'] == f'{neighbour.uuid}'

    async def test_user_delete_401(self, user):
        """Test user delete by non-authenticated user."""
        await self.make_delete(
            self.url.format(uuid=user.uuid), None, status_code=status.HTTP_401_UNAUTHORIZED,
        )

    async def test_user_delete_404(self, director):
        """Test user delete for unknown user."""
        await self.make_delete(
            self.url.format(uuid=self.unknown_uuid), director.username, status_code=status.HTTP_404_NOT_FOUND,
        )
