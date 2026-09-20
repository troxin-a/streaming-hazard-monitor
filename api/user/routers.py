from uuid import UUID

from fastapi import Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.auth.auth import current_director, JWTBearer
from api.user.sessions import UserSession
from api.user.urls import user_url

from shared.base.responses import responses
from shared.base.router import FastAPIRouter
from shared.config.session import get_async_session
from shared.user.models import UserDB
from shared.user.schemes import UserCreateScheme, UserListScheme, UserSavedScheme, UserScheme, UserUpdateScheme

user_router = FastAPIRouter(dependencies=[Depends(JWTBearer())])


@user_router.get(
    user_url.users_list,
    response_model=Page[UserListScheme],
    responses=responses(Page[UserListScheme]),
    description='Users list',
)
async def users_list(
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user)
) -> Page[UserDB]:
    """Users list."""
    return await UserSession(session).get_users(user)


@user_router.post(
    user_url.user_create,
    response_model=UserSavedScheme,
    responses=responses(
        UserSavedScheme,
        response_status=status.HTTP_201_CREATED,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
    ),
    status_code=status.HTTP_201_CREATED,
    description='Create user',
)
async def create_user(
        body: UserCreateScheme,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user),
) -> UserDB:
    """Create user."""
    return await UserSession(session).create_user(body, user)


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
    return await UserSession(session).get_user(user.uuid, user)


@user_router.get(
    user_url.user_detail,
    response_model=UserScheme,
    responses=responses(UserScheme, statuses=[status.HTTP_404_NOT_FOUND]),
    description='Get user',
)
async def get_user(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user),
) -> UserDB:
    """Get user by uuid."""
    return await UserSession(session).get_user(uuid, user)


@user_router.patch(
    user_url.user_update,
    response_model=UserSavedScheme,
    responses=responses(UserSavedScheme, statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]),
    description='Update user',
)
async def update_user(
        uuid: UUID,
        body: UserUpdateScheme,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user),
) -> UserDB:
    """Update user."""
    return await UserSession(session).update_user(uuid, body, user)


@user_router.delete(
    user_url.user_delete,
    response_model=None,
    responses=responses(
        None,
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Delete user',
)
async def delete_user(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(current_director),
) -> None:
    """Delete user."""
    await UserSession(session).delete_user(uuid, user)
