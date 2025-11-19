from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemes import LoginScheme, LoginResponseScheme, RefreshScheme, RegistrationResponseScheme, \
    RegistrationRequestScheme
from src.auth.sessions import AuthSession
from src.auth.urls import auth_url
from src.base.responses import responses
from src.base.router import FastAPIRouter
from src.config.session import get_async_session
from src.user.sessions import UserSession

auth_router = FastAPIRouter()


@auth_router.post(
    auth_url.registration,
    response_model=RegistrationResponseScheme,
    responses=responses(RegistrationResponseScheme),
    description='Registration',
)
async def registration(
        body: RegistrationRequestScheme,
        session: AsyncSession = Depends(get_async_session)
) -> RegistrationResponseScheme:
    """Login."""
    user_register = await UserSession(session).create_user(body)
    return user_register


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
