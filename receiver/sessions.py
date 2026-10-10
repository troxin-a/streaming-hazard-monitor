from uuid import UUID

from sqlalchemy import select

from shared.base.sessions import BaseSession
from shared.device.models import DeviceDB


class TelemetrySession(BaseSession):
    """Telemetry session."""

    async def get_device_uuid(self, key_hash: str) -> UUID | None:
        """Get uuid of the device the api key hash belongs to."""
        async with self.session.begin():
            query = select(DeviceDB.uuid).filter_by(key_hash=key_hash)
            return await self.session.scalar(query)
