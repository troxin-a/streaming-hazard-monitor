from uuid import UUID

from sqlalchemy import select

from shared.base.sessions import BaseSession
from shared.device.models import DeviceDB


class TelemetrySession(BaseSession):
    """Telemetry session."""

    async def get_devices(self) -> dict[str, UUID]:
        """Get all devices."""
        async with self.session.begin():
            query = select(DeviceDB)
            devices = await self.session.stream_scalars(query)

            devices_dict = {}
            async for device in devices:
                if device.key_hash:
                    devices_dict[device.key_hash] = device.uuid

            return devices_dict
