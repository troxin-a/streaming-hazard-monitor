from uuid import UUID

from fastapi import Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.auth.auth import JWTBearer
from api.user.sessions import UserSession
from api.user.urls import user_url

from shared.base.responses import responses
from shared.base.router import FastAPIRouter
from shared.config.session import get_async_session
from shared.user.models import UserDB
from shared.user.schemes import UserListScheme, UserScheme

user_router = FastAPIRouter(dependencies=[Depends(JWTBearer())])


@user_router.get(
    user_url.users_list,
    response_model=Page[UserListScheme],
    responses=responses(Page[UserListScheme]),
    description='Users list',
)
async def users_list(
        session: AsyncSession = Depends(get_async_session),
        _: UserDB = Depends(JWTBearer().current_user)
) -> Page[UserDB]:
    """Users list."""
    return await UserSession(session).get_users()


@user_router.get(
    user_url.current_user,
    response_model=UserScheme,
    responses=responses(UserScheme),
    description='Current user',
)
async def current_user(
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user),
) -> UserDB:
    """Current user."""
    return await UserSession(session).get_user(user.uuid)


@user_router.get(
    user_url.user_detail,
    response_model=UserScheme,
    responses=responses(UserScheme, statuses=[status.HTTP_404_NOT_FOUND]),
    description='Get user',
)
async def get_user(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        _: UserDB = Depends(JWTBearer().current_user),
) -> UserDB:
    """Get user by uuid."""
    return await UserSession(session).get_user(uuid)
