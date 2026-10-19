import time
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from starlette.websockets import WebSocket, WebSocketDisconnect

from shared.user.models import UserDB


@dataclass(slots=True)
class DeviceWebSocket:
    """Open websocket of the user watching the devices."""
    user: UserDB
    devices: set[UUID] = field(default_factory=set)
    sent_at: float = field(default_factory=time.time)


class DeviceWebSockets:
    """Open websockets of the users watching the devices."""

    def __init__(self) -> None:
        self.websockets: dict[WebSocket, DeviceWebSocket] = {}

    def add(self, websocket: WebSocket, user: UserDB) -> None:
        """Add the websocket of the user."""
        self.websockets[websocket] = DeviceWebSocket(user)

    def subscribe(self, websocket: WebSocket, devices: set[UUID]) -> None:
        """Replace the devices the websocket watches."""
        state = self.websockets.get(websocket)
        if state is not None:
            state.devices = devices

    def remove(self, websocket: WebSocket) -> None:
        """Remove the websocket."""
        self.websockets.pop(websocket, None)

    def has_subscriptions(self) -> bool:
        """Tell whether any websocket watches devices."""
        return any(state.devices for state in self.websockets.values())

    async def send(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """Send the message to the websocket or remove the websocket when it is closed."""
        try:
            await websocket.send_json(message)
        except (WebSocketDisconnect, RuntimeError):
            self.remove(websocket)
        else:
            state = self.websockets.get(websocket)
            if state is not None:
                state.sent_at = time.time()


device_websockets = DeviceWebSockets()
