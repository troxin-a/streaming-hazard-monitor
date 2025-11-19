from fastapi import Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src import UserDB
from src.auth.auth import JWTBearer
from src.base.responses import responses
from src.base.router import FastAPIRouter
from src.config.session import get_async_session
from src.user.schemes import UserListScheme
from src.user.sessions import UserSession
from src.user.urls import user_url

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
