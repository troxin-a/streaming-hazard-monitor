from uuid import UUID

from fastapi import Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.auth.auth import current_superuser, JWTBearer
from api.building.sessions import BuildingSession
from api.building.urls import building_url
from shared.base.responses import responses
from shared.base.router import FastAPIRouter
from shared.building.models import BuildingDB
from shared.building.schemes import BuildingCreateScheme, BuildingScheme, BuildingUpdateScheme
from shared.config.session import get_async_session
from shared.user.models import UserDB

building_router = FastAPIRouter(dependencies=[Depends(JWTBearer())])


@building_router.get(
    building_url.buildings_list,
    response_model=Page[BuildingScheme],
    responses=responses(Page[BuildingScheme]),
    description='Buildings list',
)
async def buildings_list(
        session: AsyncSession = Depends(get_async_session),
        _: UserDB = Depends(JWTBearer().current_user),
) -> Page[BuildingDB]:
    """Buildings list."""
    return await BuildingSession(session).get_buildings()


@building_router.get(
    building_url.building_detail,
    response_model=BuildingScheme,
    responses=responses(BuildingScheme, statuses=[status.HTTP_404_NOT_FOUND]),
    description='Building detail',
)
async def building_detail(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        _: UserDB = Depends(JWTBearer().current_user),
) -> BuildingDB:
    """Building detail."""
    return await BuildingSession(session).get_building(uuid)


@building_router.post(
    building_url.building_create,
    response_model=BuildingScheme,
    responses=responses(
        BuildingScheme,
        response_status=status.HTTP_201_CREATED,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
    ),
    status_code=status.HTTP_201_CREATED,
    description='Create building',
)
async def building_create(
        body: BuildingCreateScheme,
        session: AsyncSession = Depends(get_async_session),
        _: UserDB = Depends(current_superuser),
) -> BuildingDB:
    """Create building."""
    return await BuildingSession(session).create_building(body)


@building_router.patch(
    building_url.building_detail,
    response_model=BuildingScheme,
    responses=responses(BuildingScheme, statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]),
    description='Update building',
)
async def building_update(
        uuid: UUID,
        body: BuildingUpdateScheme,
        session: AsyncSession = Depends(get_async_session),
        _: UserDB = Depends(current_superuser),
) -> BuildingDB:
    """Update building."""
    return await BuildingSession(session).update_building(uuid, body)


@building_router.delete(
    building_url.building_detail,
    response_model=None,
    responses=responses(
        None,
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Delete building',
)
async def building_delete(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        _: UserDB = Depends(current_superuser),
) -> None:
    """Delete building."""
    await BuildingSession(session).delete_building(uuid)
