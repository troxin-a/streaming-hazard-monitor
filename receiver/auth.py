from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
from starlette.requests import Request

from shared.device.services import hash_api_key

api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)


async def current_device_uuid(
        request: Request,
        key: str | None = Depends(api_key_header),
) -> UUID:
    """Return uuid of the device the api key of the request belongs to."""
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Api key is required')
    device_uuid = request.state.devices.get(hash_api_key(key), None)
    if device_uuid is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid api key')
    return device_uuid
