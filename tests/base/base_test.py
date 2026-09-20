import json
from typing import Any

from httpx import AsyncClient, ASGITransport
from starlette import status

from api.auth.services.utils import HashPassword
from api.main import app


class BaseTestCase:
    """Base class for testing the entire project."""
    base_url = 'http://test/api'
    access_token: str = ''
    refresh_token: str = ''
    transport = ASGITransport(app=app)
    password: str = '123qwe456rty!S'
    hashed_password = HashPassword.hash_password(password)

    async def _login(self, username: str) -> tuple[str, str]:
        """Login."""
        async with AsyncClient(transport=self.transport, base_url=self.base_url) as client:
            client_data = {'username': username, 'password': self.password}
            response = await client.post('/auth/login/', json=client_data)
            response_data = response.json() or {}
            access, refresh = response_data.get('access', ''), response_data.get('refresh', '')
            self.access_token = access
            self.refresh_token = refresh
            return self.access_token, self.refresh_token

    async def _make_request(
            self,
            method: str,
            url: str,
            username: str | None = None,
            data: object = None,
            status_code: int = status.HTTP_200_OK,
            headers: dict = None
    ) -> dict | None:
        """Method for generating a request with authorization."""
        async with AsyncClient(transport=self.transport, base_url=self.base_url, follow_redirects=True) as client:
            url = f'{self.base_url}{url}'

            headers_to_send = {'content-type': 'application/json'}
            if username:
                await self._login(username)
                if self.access_token:
                    headers_to_send.update({'Authorization': f'Bearer {self.access_token}'})
            if headers is not None:
                headers_to_send.update(headers)
            client.headers = headers_to_send

            request_data = None
            if data and method.lower() != 'get':
                request_data = json.dumps(data)

            response = await client.request(method, url, content=request_data, follow_redirects=True, params=data)
            assert response is not None
            assert response.status_code == status_code, f'status: {response.status_code}, response: {response.text}'

            if method != 'DELETE' and response.status_code != status.HTTP_204_NO_CONTENT:
                return response.json()

    async def make_post(
            self,
            url: str,
            username: str | None,
            data: Any = None,
            status_code: int = status.HTTP_200_OK,
            headers: dict = None
    ) -> dict:
        """Make post method."""
        if data is None:
            data = {}
        return await self._make_request('POST', url, username, data, status_code, headers)

    async def make_get(
            self,
            url: str,
            username: str | None = None,
            params: dict = None,
            status_code: int = status.HTTP_200_OK,
            headers: dict = None
    ) -> dict:
        """Make get method."""
        return await self._make_request('GET', url, username, params, status_code, headers)

    async def make_patch(
            self,
            url: str,
            username: str | None,
            data: dict,
            status_code: int = status.HTTP_200_OK,
            headers: dict = None
    ) -> dict:
        """Make patch method."""
        return await self._make_request('PATCH', url, username, data, status_code, headers)

    async def make_put(
            self,
            url: str,
            username: str | None,
            data: dict,
            status_code: int = status.HTTP_200_OK,
            headers: dict = None
    ) -> dict:
        """Make put method."""
        return await self._make_request('PUT', url, username, data, status_code, headers)

    async def make_delete(
            self,
            url: str,
            username: str | None,
            data: dict = None,
            status_code: int = status.HTTP_204_NO_CONTENT,
            headers: dict = None
    ) -> None:
        """Make delete method."""
        return await self._make_request('DELETE', url, username, data, status_code, headers)
