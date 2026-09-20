from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.schemes import LoginScheme, LoginResponseScheme, RefreshScheme
from api.auth.sessions import AuthSession
from api.auth.urls import auth_url
from shared.base.responses import responses
from shared.base.router import FastAPIRouter
from shared.config.session import get_async_session

auth_router = FastAPIRouter()


@auth_router.post(
    auth_url.login,
    response_model=LoginResponseScheme,
    responses=responses(LoginResponseScheme),
    description='Login',
)
async def login(
        body: LoginScheme,
        session: AsyncSession = Depends(get_async_session)
) -> LoginResponseScheme:
    """Login."""
    user_login = await AuthSession(session).login_user(body)
    return user_login


@auth_router.post(
    auth_url.refresh,
    response_model=LoginResponseScheme,
    responses=responses(LoginResponseScheme),
    description='Refresh Token'
)
async def refresh(
        body: RefreshScheme,
        session: AsyncSession = Depends(get_async_session),
) -> LoginResponseScheme:
    """Refresh token."""
    refresh_token = body.refresh
    token = await AuthSession(session).check_refresh_token(refresh_token)
    return token
