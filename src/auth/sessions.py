from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from src.auth.schemes import LoginResponseScheme, LoginScheme
from src.auth.services.token import AccessToken, RefreshToken
from src.auth.services.utils import HashPassword
from src.base.sessions import BaseSession
from src.user.models import UserDB


class AuthSession(BaseSession):
    """Auth session."""

    async def login_user(self, body: LoginScheme) -> LoginResponseScheme:
        """login user."""
        username, password, remember_me = body.username, body.password, body.remember_me
        async with self.session.begin():
            query = select(UserDB).filter_by(username=username)
            user = await self.session.scalar(query)
            if user:
                check_password = HashPassword.check_password(user.password, password)
                if check_password:
                    access = AccessToken.for_user(user)
                    refresh = RefreshToken.for_user(user, remember_me=remember_me)
                    return LoginResponseScheme(access=access, refresh=refresh)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')

    async def check_refresh_token(self, token: str) -> LoginResponseScheme:
        """Check refresh token."""
        async with self.session.begin():
            refresh_token = RefreshToken(token)
            payload = refresh_token.payload
            access, refresh = refresh_token.update_tokens(payload)
            return LoginResponseScheme(access=access, refresh=refresh)
