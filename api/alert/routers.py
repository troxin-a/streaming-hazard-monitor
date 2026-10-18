from fastapi import Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from api.alert.sessions import AlertSession
from api.alert.urls import alert_url
from api.auth.auth import JWTBearer
from shared.alert.models import AlertDB
from shared.alert.schemes import AlertScheme
from shared.base.responses import responses
from shared.base.router import FastAPIRouter
from shared.config.session import get_async_session
from shared.user.models import UserDB

alert_router = FastAPIRouter(dependencies=[Depends(JWTBearer())])


@alert_router.get(
    alert_url.alerts_list,
    response_model=Page[AlertScheme],
    responses=responses(Page[AlertScheme]),
    description='Alerts list',
)
async def alerts_list(
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user),
) -> Page[AlertDB]:
    """Alerts list."""
    return await AlertSession(session).get_alerts(user)
