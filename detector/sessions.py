import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, insert, literal, select, update
from sqlalchemy.sql.functions import coalesce

from shared.alert.models import AlertDB
from shared.base.sessions import BaseSession
from shared.device.enums import AlertLevel
from shared.device.models import DefaultThresholdDB, DeviceDB, DeviceThresholdDB
from shared.reading.schemes import ReadingMessageScheme

logger = logging.getLogger(__name__)


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

    async def get_levels(self) -> dict[UUID, AlertLevel]:
        """Get the level of the alert in progress of every device that has one."""
        async with self.session.begin():
            query = select(AlertDB.device_uuid, AlertDB.level).where(AlertDB.ended_at.is_(None))
            rows = await self.session.stream(query)
            return {row.device_uuid: row.level async for row in rows}

    async def change_level(self, reading: ReadingMessageScheme, level: AlertLevel | None) -> None:
        """End the alert in progress of the device of the reading and start the alert of the level."""
        async with self.session.begin():
            query = (
                update(AlertDB)
                .where(AlertDB.device_uuid == reading.device_uuid, AlertDB.ended_at.is_(None))
                .values(ended_at=reading.received_at)
            )
            await self.session.execute(query)
            if level is None:
                return

            columns = [AlertDB.device_uuid, AlertDB.building_uuid, AlertDB.level, AlertDB.value, AlertDB.started_at]
            alert = select(
                DeviceDB.uuid,
                DeviceDB.building_uuid,
                literal(level, AlertDB.level.type),
                literal(reading.value, AlertDB.value.type),
                literal(reading.received_at, AlertDB.started_at.type),
            ).filter_by(uuid=reading.device_uuid)
            query = insert(AlertDB).from_select(columns, alert).returning(AlertDB.uuid)
            if await self.session.scalar(query) is None:
                logger.warning('Alert is not saved: device %s is not found', reading.device_uuid)
