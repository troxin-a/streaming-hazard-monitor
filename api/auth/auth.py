from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.auth.services.token import AccessToken
from api.user.sessions import UserSession
from shared.config.session import get_async_session
from shared.user.models import UserDB


class JWTBearer(HTTPBearer):
    """JWT Bearer."""

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        payload_access_token = await self.get_payload_access_token(credentials.credentials)
        return payload_access_token

    @classmethod
    async def get_payload_access_token(cls, token: str) -> dict:
        """Get payload access token."""
        payload = AccessToken(token).payload
        if payload.get('token_type') != 'access':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authorization token')
        return payload

    @classmethod
    async def current_user(
            cls,
            request: Request,
            session: AsyncSession = Depends(get_async_session),
    ) -> UserDB | None:
        """Current user."""
        credentials: HTTPAuthorizationCredentials = await super().__call__(cls, request)
        token = credentials.credentials
        payload = AccessToken(token).payload
        user_uuid = payload.get('user_uuid')
        user = await UserSession(session).get_user_by_uuid(uuid=user_uuid)
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User inactive')
        return user
