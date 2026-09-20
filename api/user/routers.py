from fastapi import Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.auth import JWTBearer
from api.user.sessions import UserSession
from api.user.urls import user_url

from shared.base.responses import responses
from shared.base.router import FastAPIRouter
from shared.config.session import get_async_session
from shared.user.models import UserDB
from shared.user.schemes import UserListScheme

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
