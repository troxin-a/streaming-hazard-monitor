from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
from starlette.requests import Request

from shared.device.services import hash_api_key

api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)


def get_devices(request: Request) -> dict[str, UUID]:
    """Return device uuids by the hashes of their api keys loaded by the running application."""
    return request.state.devices


async def current_device_uuid(
        key: str | None = Depends(api_key_header),
        devices: dict[str, UUID] = Depends(get_devices),
) -> UUID:
    """Return uuid of the device the api key of the request belongs to."""
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Api key is required')
    device_uuid = devices.get(hash_api_key(key))
    if device_uuid is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid api key')
    return device_uuid
