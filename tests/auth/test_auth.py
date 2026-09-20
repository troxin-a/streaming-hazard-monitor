from starlette import status

from tests.base.base_test import BaseTestCase


class TestCaseAuth(BaseTestCase):
    """Test Auth."""
    user_url = '/auth'

    async def test_login(self, user):
        """Test login."""
        url = f'{self.user_url}/login/'
        data = {'username': user.username, 'password': self.password}
        response = await self.make_post(url, None, data, status.HTTP_200_OK)
        assert response['access'] is not None
        assert response['refresh'] is not None
        return response

    async def test_login_401(self, user):
        """Test login negative."""
        url = f'{self.user_url}/login/'
        data = {'username': user.username, 'password': f'{self.password}{self.password}'}
        await self.make_post(url, None, data, status.HTTP_401_UNAUTHORIZED)
        data = {'username': f'{user.username}{user.username}', 'password': f'{self.password}'}
        await self.make_post(url, None, data, status.HTTP_401_UNAUTHORIZED)

    async def test_refresh_token(self, user):
        """Test refresh token."""
        response_login = await self.test_login(user)
        refresh = response_login.get('refresh')

        url = f'{self.user_url}/token/refresh/'
        response = await self.make_post(url, user.username, {'refresh': refresh}, status.HTTP_200_OK)
        assert response.get('access') is not None
        assert response.get('refresh') is not None

    async def test_refresh_token_401(self, user):
        """Test refresh token negative."""
        response_login = await self.test_login(user)
        access, refresh = response_login.get('access'), response_login.get('refresh')

        url = f'{self.user_url}/token/refresh/'
        await self.make_post(url, user.username, {'refresh': access}, status.HTTP_401_UNAUTHORIZED)
        await self.make_post(url, user.username, {'refresh': f'{refresh}1'}, status.HTTP_401_UNAUTHORIZED)
        await self.make_post(url, user.username, {}, status.HTTP_422_UNPROCESSABLE_CONTENT)
