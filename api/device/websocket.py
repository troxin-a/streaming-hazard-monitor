import time
from typing import Any
from uuid import UUID

from starlette.websockets import WebSocket, WebSocketDisconnect

from shared.user.models import UserDB


class DeviceWebSockets:
    """Open websockets of the users watching the devices."""

    def __init__(self) -> None:
        self.users: dict[WebSocket, UserDB] = {}
        self.devices: dict[WebSocket, set[UUID]] = {}
        self.sent_at: dict[WebSocket, float] = {}

    def add(self, websocket: WebSocket, user: UserDB) -> None:
        """Add the websocket of the user."""
        self.users[websocket] = user
        self.sent_at[websocket] = time.time()

    def subscribe(self, websocket: WebSocket, devices: set[UUID]) -> None:
        """Replace the devices the websocket watches."""
        self.devices[websocket] = devices

    def remove(self, websocket: WebSocket) -> None:
        """Remove the websocket."""
        self.users.pop(websocket, None)
        self.devices.pop(websocket, None)
        self.sent_at.pop(websocket, None)

    async def send(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """Send the message to the websocket or remove the websocket when it is closed."""
        try:
            await websocket.send_json(message)
        except (WebSocketDisconnect, RuntimeError):
            self.remove(websocket)
        else:
            self.sent_at[websocket] = time.time()


device_websockets = DeviceWebSockets()
