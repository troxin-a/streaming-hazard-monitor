from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from receiver.sessions import TelemetrySession
from shared.config.session import get_async_session
from shared.device.services import hash_api_key

api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)


async def current_device_uuid(
        key: str | None = Depends(api_key_header),
        session: AsyncSession = Depends(get_async_session),
) -> UUID:
    """Return uuid of the device the api key of the request belongs to."""
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Api key is required')
    device_uuid = await TelemetrySession(session).get_device_uuid(hash_api_key(key))
    if device_uuid is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid api key')
    return device_uuid
