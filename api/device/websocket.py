import logging
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.device.sessions import DeviceSession
from shared.alert.schemes import LevelChangeMessageScheme
from shared.config.session import async_session_maker
from shared.device.schemes import DeviceLevelScheme
from shared.user.enums import UserRole
from shared.user.models import UserDB

logger = logging.getLogger(__name__)


def can_see(user: UserDB, building_uuid: UUID, company_uuid: UUID) -> bool:
    """Check the user is allowed to see the devices of the building of the company."""
    if user.is_superuser:
        return True
    if user.role == UserRole.DIRECTOR:
        return user.company_uuid == company_uuid
    return user.building_uuid == building_uuid


class LevelWebSockets:
    """Open websockets of the users watching the levels of the devices."""

    def __init__(self) -> None:
        self.users: dict[WebSocket, UserDB] = {}

    def add(self, websocket: WebSocket, user: UserDB) -> None:
        """Add the websocket of the user."""
        self.users[websocket] = user

    def remove(self, websocket: WebSocket) -> None:
        """Remove the websocket."""
        self.users.pop(websocket, None)

    async def send(self, change: LevelChangeMessageScheme, building_uuid: UUID, company_uuid: UUID) -> None:
        """Send the level change of the device to the users who are allowed to see it."""
        message = DeviceLevelScheme.model_validate(change, from_attributes=True).model_dump(mode='json')
        for websocket, user in list(self.users.items()):
            if not can_see(user, building_uuid, company_uuid):
                continue
            try:
                await websocket.send_json(message)
            except (WebSocketDisconnect, RuntimeError):
                self.remove(websocket)


level_websockets = LevelWebSockets()


async def send_level_changes(changes: list[LevelChangeMessageScheme]) -> None:
    """Send the level changes of the devices to the websockets of the users who are allowed to see them."""
    if not level_websockets.users:
        return
    try:
        async with async_session_maker() as session:
            places = await DeviceSession(session).get_device_places({change.device_uuid for change in changes})
    except (SQLAlchemyError, OSError):
        logger.warning('Level changes are not sent: the database is unavailable', exc_info=True)
        return
    for change in changes:
        place = places.get(change.device_uuid)
        if place is not None:
            await level_websockets.send(change, place.building_uuid, place.company_uuid)
