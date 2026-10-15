import logging
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import insert, select, update, Values

from detector.devices_state import DeviceState
from shared.alert.models import AlertDB
from shared.base.sessions import BaseSession
from shared.device.enums import AlertLevel, DeviceType
from shared.device.models import DefaultThresholdDB, DeviceDB, DeviceThresholdDB
from shared.reading.schemes import ReadingMessageScheme

logger = logging.getLogger(__name__)


class DetectorSession(BaseSession):
    """Threshold detector session."""

    async def get_states(self) -> dict[UUID, DeviceState]:
        """Get the state of every device with thresholds and the level of its alert in progress."""
        async with self.session.begin():
            states = await self.get_thresholds()
            levels = await self.get_levels()
            for device_uuid, level in levels.items():
                state = states.get(device_uuid)
                if state is not None:
                    state.level = level
            return states

    async def get_thresholds(self) -> dict[UUID, DeviceState]:
        """Get the state of every device with thresholds: the ones set for it or the default ones of its type."""
        defaults = await self.get_default_thresholds()
        query = (
            select(DeviceDB.uuid, DeviceDB.type, DeviceThresholdDB.level, DeviceThresholdDB.value)
            .outerjoin(DeviceThresholdDB, DeviceThresholdDB.device_uuid == DeviceDB.uuid)
        )
        rows = await self.session.stream(query)

        states: dict[UUID, DeviceState] = {}
        async for row in rows:
            if row.level is None:
                type_defaults = defaults.get(row.type)
                if type_defaults is not None:
                    states[row.uuid] = DeviceState(thresholds=type_defaults)
                continue
            state = states.get(row.uuid)
            if state is None:
                state = states[row.uuid] = DeviceState(thresholds={})
            state.thresholds[row.level] = row.value

        return states

    async def get_default_thresholds(self) -> dict[DeviceType, dict[AlertLevel, Decimal]]:
        """Get default thresholds of every device type."""
        query = select(DefaultThresholdDB.device_type, DefaultThresholdDB.level, DefaultThresholdDB.value)
        defaults: dict[DeviceType, dict[AlertLevel, Decimal]] = {}
        async for row in await self.session.stream(query):
            defaults.setdefault(row.device_type, {})[row.level] = row.value
        return defaults

    async def get_levels(self) -> dict[UUID, AlertLevel]:
        """Get the level of the alert in progress of every device that has one."""
        query = select(AlertDB.device_uuid, AlertDB.level).where(AlertDB.ended_at.is_(None))
        rows = await self.session.stream(query)
        return {row.device_uuid: row.level async for row in rows}

    async def change_level(self, readings: list[tuple[ReadingMessageScheme, AlertLevel | None]]) -> None:
        """End the alert in progress of the device of the reading and start the alert of the level."""
        async with self.session.begin():
            ended = Values(
                AlertDB.device_uuid,
                AlertDB.ended_at,
                name='ended',
            ).data([(reading.device_uuid, reading.received_at) for reading, level in readings])
            update_stmt = (
                update(AlertDB)
                .where(AlertDB.device_uuid == ended.c.device_uuid, AlertDB.ended_at.is_(None))
                .values(ended_at=ended.c.ended_at)
            )
            await self.session.execute(update_stmt)

            data = [
                (reading.device_uuid, reading.value, reading.received_at, level, uuid4())
                for reading, level in readings
                if level is not None
            ]
            if not data:
                return
            started = Values(
                AlertDB.device_uuid, AlertDB.value, AlertDB.started_at, AlertDB.level, AlertDB.uuid,
                name='started'
            ).data(data)
            to_create = [i[0] for i in data]
            query = (
                select(
                    started.c.uuid,
                    started.c.level,
                    started.c.value,
                    started.c.started_at,
                    started.c.device_uuid,
                    DeviceDB.building_uuid,
                )
                .join(started, DeviceDB.uuid == started.c.device_uuid)
            )
            columns = [
                AlertDB.uuid, AlertDB.level, AlertDB.value,
                AlertDB.started_at, AlertDB.device_uuid, AlertDB.building_uuid,
            ]
            stmt = insert(AlertDB).from_select(columns, query).returning(AlertDB.device_uuid)
            result = set(await self.session.scalars(stmt))

            for uuid in to_create:
                if uuid not in result:
                    logger.warning('Alert is not saved: device %s is not found', uuid)
