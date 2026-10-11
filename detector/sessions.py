from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.sql.functions import coalesce

from shared.base.sessions import BaseSession
from shared.device.enums import AlertLevel
from shared.device.models import DefaultThresholdDB, DeviceDB, DeviceThresholdDB


class DetectorSession(BaseSession):
    """Threshold detector session."""

    async def get_thresholds(self) -> dict[UUID, dict[AlertLevel, Decimal]]:
        """Get thresholds of every device: the ones set for it or the default ones of its type."""
        async with self.session.begin():
            own, default = DeviceThresholdDB, DefaultThresholdDB
            query = (
                select(
                    DeviceDB.uuid,
                    coalesce(own.level, default.level).label('level'),
                    coalesce(own.value, default.value).label('value'),
                )
                .select_from(DeviceDB)
                .outerjoin(own, own.device_uuid == DeviceDB.uuid)
                .outerjoin(default, and_(default.device_type == DeviceDB.type, own.uuid.is_(None)))
            )
            rows = await self.session.stream(query)

            thresholds: dict[UUID, dict[AlertLevel, Decimal]] = {}
            async for row in rows:
                if row.level is not None:
                    thresholds.setdefault(row.uuid, {})[row.level] = row.value

            return thresholds
