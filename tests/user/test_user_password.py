import pytest
from starlette import status

from tests.base.base_test import BaseTestCase

pytestmark = pytest.mark.integration

NEW_PASSWORD = 'qwerty123!S'


class TestCaseUserPassword(BaseTestCase):
    """Own password change test suite."""
    url = '/user/me/password/'

    async def test_user_changes_own_password(self, user):
        """Test a user changes their own password and logs in with the new one."""
        data = {'old_password': self.password, 'password1': NEW_PASSWORD, 'password2': NEW_PASSWORD}
        await self.make_post(self.url, user.username, data, status.HTTP_204_NO_CONTENT)

        self.password = NEW_PASSWORD
        access, _ = await self._login(user.username)
        assert access

    async def test_user_password_old_one_stops_working(self, user):
        """Test the previous password is rejected after the change."""
        data = {'old_password': self.password, 'password1': NEW_PASSWORD, 'password2': NEW_PASSWORD}
        await self.make_post(self.url, user.username, data, status.HTTP_204_NO_CONTENT)

        access, _ = await self._login(user.username)
        assert not access

    async def test_user_password_wrong_old_password(self, user):
        """Test the password stays the same when the current one is wrong."""
        data = {'old_password': 'wrong', 'password1': NEW_PASSWORD, 'password2': NEW_PASSWORD}
        response = await self.make_post(self.url, user.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)
        assert response['detail'] == [{'field': 'old_password', 'message': 'Incorrect password'}]

        access, _ = await self._login(user.username)
        assert access

    async def test_user_password_mismatch(self, user):
        """Test own password change with different new passwords."""
        data = {'old_password': self.password, 'password1': NEW_PASSWORD, 'password2': 'another'}
        response = await self.make_post(self.url, user.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)
        assert response['detail'] == [{'field': 'password1', 'message': 'Passwords must be the same'}]

    async def test_user_password_empty(self, user):
        """Test own password change with an empty new password."""
        data = {'old_password': self.password, 'password1': '', 'password2': ''}
        await self.make_post(self.url, user.username, data, status.HTTP_422_UNPROCESSABLE_CONTENT)

    async def test_user_password_401(self, user):
        """Test own password change by non-authenticated user."""
        data = {'old_password': self.password, 'password1': NEW_PASSWORD, 'password2': NEW_PASSWORD}
        await self.make_post(self.url, None, data, status.HTTP_401_UNAUTHORIZED)

    async def test_user_password_405(self, user):
        """Test own password change wrong request method."""
        await self.make_get(self.url, user.username, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
