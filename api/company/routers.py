from uuid import UUID

from fastapi import Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.auth.auth import current_director, current_superuser, JWTBearer
from api.company.sessions import CompanySession
from api.company.urls import company_url
from shared.base.responses import responses
from shared.base.router import FastAPIRouter
from shared.company.models import CompanyDB
from shared.company.schemes import CompanyCreateScheme, CompanyScheme, CompanyUpdateScheme
from shared.config.session import get_async_session
from shared.user.models import UserDB

company_router = FastAPIRouter(dependencies=[Depends(JWTBearer())])


@company_router.get(
    company_url.companies_list,
    response_model=Page[CompanyScheme],
    responses=responses(Page[CompanyScheme]),
    description='Companies list',
)
async def companies_list(
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user),
) -> Page[CompanyDB]:
    """Companies list."""
    return await CompanySession(session).get_companies(user)


@company_router.post(
    company_url.company_create,
    response_model=CompanyScheme,
    responses=responses(
        CompanyScheme,
        response_status=status.HTTP_201_CREATED,
        statuses=[status.HTTP_409_CONFLICT],
    ),
    status_code=status.HTTP_201_CREATED,
    description='Create company',
)
async def company_create(
        body: CompanyCreateScheme,
        session: AsyncSession = Depends(get_async_session),
        _: UserDB = Depends(current_superuser),
) -> CompanyDB:
    """Create company."""
    return await CompanySession(session).create_company(body)


@company_router.get(
    company_url.company_detail,
    response_model=CompanyScheme,
    responses=responses(CompanyScheme, statuses=[status.HTTP_404_NOT_FOUND]),
    description='Company detail',
)
async def company_detail(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user),
) -> CompanyDB:
    """Company detail."""
    return await CompanySession(session).get_company(uuid, user)


@company_router.patch(
    company_url.company_detail,
    response_model=CompanyScheme,
    responses=responses(CompanyScheme, statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]),
    description='Update company',
)
async def company_update(
        uuid: UUID,
        body: CompanyUpdateScheme,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(current_director),
) -> CompanyDB:
    """Update company."""
    return await CompanySession(session).update_company(uuid, body, user)


@company_router.delete(
    company_url.company_delete,
    response_model=None,
    responses=responses(
        None,
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Delete company',
)
async def company_delete(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        _: UserDB = Depends(current_superuser),
) -> None:
    """Delete company."""
    await CompanySession(session).delete_company(uuid)
