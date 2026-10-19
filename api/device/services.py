import logging
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from api.device.sessions import DeviceSession
from api.device.websocket import device_websockets
from shared.alert.schemes import LevelChangeMessageScheme
from shared.config.session import async_session_maker
from shared.device.schemes import DeviceLevelScheme, DeviceReadingsScheme, DeviceSubscribeScheme
from shared.reading.schemes import ReadingMessageScheme
from shared.user.models import UserDB

logger = logging.getLogger(__name__)


async def handle_message(websocket: WebSocket, user: UserDB, text: str, session: AsyncSession) -> None:
    """Subscribe the websocket to the devices of the message the user is allowed to see."""
    try:
        message = DeviceSubscribeScheme.model_validate_json(text)
        devices = await DeviceSession(session).get_visible_device_uuids(user, set(message.devices))
    except ValidationError as error:
        logger.warning(f'Websocket message does not match {DeviceSubscribeScheme.__name__}: {error}')
        return
    except (SQLAlchemyError, OSError) as error:
        logger.warning(f'Subscription is not changed: the database is unavailable: {error}')
        return
    device_websockets.subscribe(websocket, devices)
    logger.info(f'Websocket of {user.username} is subscribed to {len(devices)} devices')


async def broadcast_level_changes(changes: list[LevelChangeMessageScheme]) -> None:
    """Send the level changes of the devices to the users who are allowed to see them."""
    if not device_websockets.users:
        return
    try:
        async with async_session_maker() as session:
            places = await DeviceSession(session).get_device_places({change.device_uuid for change in changes})
    except (SQLAlchemyError, OSError) as error:
        logger.warning(f'Level changes are not sent: the database is unavailable: {error}')
        return
    for change in changes:
        place = places.get(change.device_uuid)
        if place is not None:
            message = DeviceLevelScheme.model_validate(change, from_attributes=True).model_dump(mode='json')
            for websocket, user in list(device_websockets.users.items()):
                if user.can_see_building(place.building_uuid, place.company_uuid):
                    await device_websockets.send(websocket, message)


async def broadcast_readings(readings: list[ReadingMessageScheme]) -> None:
    """Send every websocket the readings of the devices it watches."""
    by_device: dict[UUID, list[ReadingMessageScheme]] = {}
    for reading in readings:
        by_device.setdefault(reading.device_uuid, []).append(reading)
    for websocket, devices in list(device_websockets.devices.items()):
        items = [reading for device in devices for reading in by_device.get(device, [])]
        if items:
            await device_websockets.send(websocket, DeviceReadingsScheme(items=items).model_dump(mode='json'))
