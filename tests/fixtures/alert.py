from datetime import datetime, UTC
from typing import Sequence
from uuid import UUID

import pytest
from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared import AlertDB
from shared.device.enums import AlertLevel

ALERT_LEVEL = AlertLevel.LEVEL_2
ALERT_STARTED_AT = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)
ALERT_ENDED_AT = datetime(2026, 10, 10, 12, 5, tzinfo=UTC)


async def create_alert(
        override_get_async_session: AsyncSession,
        device_uuid: UUID,
        building_uuid: UUID,
        ended_at: datetime | None = None,
) -> AlertDB:
    """Create alert."""
    alert = AlertDB(
        device_uuid=device_uuid,
        building_uuid=building_uuid,
        level=ALERT_LEVEL,
        started_at=ALERT_STARTED_AT,
        ended_at=ended_at,
    )
    override_get_async_session.add(alert)
    await override_get_async_session.commit()
    return alert


async def get_alerts(
        override_get_async_session: AsyncSession,
) -> Sequence[Row[tuple[UUID, AlertLevel, datetime, datetime | None]]]:
    """Get saved alerts in the order they started."""
    async with override_get_async_session.begin():
        query = select(AlertDB.building_uuid, AlertDB.level, AlertDB.started_at, AlertDB.ended_at)
        return (await override_get_async_session.execute(query.order_by(AlertDB.started_at))).all()


async def get_levels(override_get_async_session: AsyncSession) -> dict[UUID, AlertLevel]:
    """Get the level of the alert in progress of every device that has one."""
    async with override_get_async_session.begin():
        query = select(AlertDB.device_uuid, AlertDB.level).where(AlertDB.ended_at.is_(None))
        return {row.device_uuid: row.level for row in await override_get_async_session.execute(query)}


@pytest.fixture(scope='function')
async def alert(override_get_async_session, device, building) -> AlertDB:
    """Alert in progress of the device fixture."""
    return await create_alert(override_get_async_session, device.uuid, building.uuid)


@pytest.fixture(scope='function')
async def ended_alert(override_get_async_session, device, building) -> AlertDB:
    """Ended alert of the device fixture."""
    return await create_alert(override_get_async_session, device.uuid, building.uuid, ALERT_ENDED_AT)
