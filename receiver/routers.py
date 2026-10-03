from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from receiver.auth import current_device_uuid
from receiver.sessions import TelemetrySession
from receiver.urls import telemetry_url
from shared.base.responses import responses
from shared.base.router import FastAPIRouter
from shared.config.session import get_async_session
from shared.reading.models import ReadingDB
from shared.reading.schemes import ReadingCreateScheme, ReadingScheme

telemetry_router = FastAPIRouter()


@telemetry_router.post(
    telemetry_url.telemetry,
    response_model=ReadingScheme,
    responses=responses(
        ReadingScheme,
        response_status=status.HTTP_201_CREATED,
        exclude=[status.HTTP_403_FORBIDDEN],
    ),
    status_code=status.HTTP_201_CREATED,
    description='Send telemetry',
)
async def send_telemetry(
        body: ReadingCreateScheme,
        session: AsyncSession = Depends(get_async_session),
        device_uuid: UUID = Depends(current_device_uuid),
) -> ReadingDB:
    """Save the reading sent by the device."""
    return await TelemetrySession(session).create_reading(device_uuid, body)
