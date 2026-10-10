from decimal import Decimal
from typing import Sequence
from uuid import UUID

from fastapi import Depends
from fastapi_pagination import Page
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.auth.auth import current_director, JWTBearer
from api.device.sessions import DeviceSession, ThresholdSession
from api.device.urls import device_url
from shared.base.responses import responses
from shared.base.router import FastAPIRouter
from shared.config.session import get_async_session
from shared.device.enums import AlertLevel
from shared.device.models import DeviceDB, DeviceThresholdDB
from shared.device.schemes import (
    DeviceAPIKeyScheme, DeviceCreateScheme, DeviceScheme, DeviceUpdateScheme, ThresholdScheme, ThresholdsSetScheme,
)
from shared.user.models import UserDB

device_router = FastAPIRouter(dependencies=[Depends(JWTBearer())])


@device_router.get(
    device_url.devices_list,
    response_model=Page[DeviceScheme],
    responses=responses(Page[DeviceScheme]),
    description='Devices list',
)
async def devices_list(
        search: str | None = None,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user),
) -> Page[DeviceDB]:
    """Devices list."""
    return await DeviceSession(session).get_devices(user, search)


@device_router.post(
    device_url.device_create,
    response_model=DeviceScheme,
    responses=responses(
        DeviceScheme,
        response_status=status.HTTP_201_CREATED,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
    ),
    status_code=status.HTTP_201_CREATED,
    description='Create device',
)
async def device_create(
        body: DeviceCreateScheme,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(current_director),
) -> DeviceDB:
    """Create device."""
    return await DeviceSession(session).create_device(body, user)


@device_router.get(
    device_url.device_detail,
    response_model=DeviceScheme,
    responses=responses(DeviceScheme, statuses=[status.HTTP_404_NOT_FOUND]),
    description='Device detail',
)
async def device_detail(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user),
) -> DeviceDB:
    """Device detail."""
    return await DeviceSession(session).get_device(uuid, user)


@device_router.patch(
    device_url.device_update,
    response_model=DeviceScheme,
    responses=responses(DeviceScheme, statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]),
    description='Update device',
)
async def device_update(
        uuid: UUID,
        body: DeviceUpdateScheme,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(current_director),
) -> DeviceDB:
    """Update device."""
    return await DeviceSession(session).update_device(uuid, body, user)


@device_router.delete(
    device_url.device_delete,
    response_model=None,
    responses=responses(
        None,
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Delete device',
)
async def device_delete(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(current_director),
) -> None:
    """Delete device."""
    await DeviceSession(session).delete_device(uuid, user)


@device_router.post(
    device_url.device_api_key_create,
    response_model=DeviceAPIKeyScheme,
    responses=responses(
        DeviceAPIKeyScheme,
        response_status=status.HTTP_201_CREATED,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
    ),
    status_code=status.HTTP_201_CREATED,
    description='Issue an api key for the device, the key is shown once',
)
async def device_api_key_create(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(current_director),
) -> DeviceAPIKeyScheme:
    """Issue an api key for the device."""
    return DeviceAPIKeyScheme(key=await DeviceSession(session).create_api_key(uuid, user))


@device_router.delete(
    device_url.device_api_key_delete,
    response_model=None,
    responses=responses(
        None,
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND],
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Revoke the api key of the device',
)
async def device_api_key_delete(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(current_director),
) -> None:
    """Revoke the api key of the device."""
    await DeviceSession(session).delete_api_key(uuid, user)


@device_router.get(
    device_url.device_thresholds_list,
    response_model=list[ThresholdScheme],
    responses=responses(list[ThresholdScheme], statuses=[status.HTTP_404_NOT_FOUND]),
    description='Thresholds of the device: the ones set for it or the default ones of its type',
)
async def device_thresholds_list(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(JWTBearer().current_user),
) -> Sequence[Row[tuple[AlertLevel, Decimal, bool]]]:
    """Thresholds of the device."""
    return await ThresholdSession(session).get_thresholds(uuid, user)


@device_router.post(
    device_url.device_thresholds_create,
    response_model=list[ThresholdScheme],
    responses=responses(
        list[ThresholdScheme],
        response_status=status.HTTP_201_CREATED,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
    ),
    status_code=status.HTTP_201_CREATED,
    description='Set thresholds of every level for the device',
)
async def device_thresholds_create(
        uuid: UUID,
        body: ThresholdsSetScheme,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(current_director),
) -> list[DeviceThresholdDB]:
    """Set thresholds for the device."""
    return await ThresholdSession(session).create_thresholds(uuid, body, user)


@device_router.patch(
    device_url.device_thresholds_update,
    response_model=list[ThresholdScheme],
    responses=responses(list[ThresholdScheme], statuses=[status.HTTP_404_NOT_FOUND]),
    description='Update thresholds of every level set for the device',
)
async def device_thresholds_update(
        uuid: UUID,
        body: ThresholdsSetScheme,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(current_director),
) -> list[DeviceThresholdDB]:
    """Update thresholds set for the device."""
    return await ThresholdSession(session).update_thresholds(uuid, body, user)


@device_router.delete(
    device_url.device_thresholds_delete,
    response_model=None,
    responses=responses(
        None,
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND],
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Delete thresholds set for the device, the default ones apply again',
)
async def device_thresholds_delete(
        uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        user: UserDB = Depends(current_director),
) -> None:
    """Delete thresholds set for the device."""
    await ThresholdSession(session).delete_thresholds(uuid, user)
