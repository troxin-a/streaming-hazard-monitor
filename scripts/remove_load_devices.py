import asyncio
from pathlib import Path

from sqlalchemy import delete, select

from scripts.create_load_devices import COMPANY_NAME, DEFAULT_OUTPUT
from shared import BuildingDB, CompanyDB, DeviceDB
from shared.config.session import async_session_maker


async def remove_load_devices(output: Path) -> None:
    """Delete the load test company with its buildings and devices and remove the api keys file."""
    company_uuids = select(CompanyDB.uuid).filter_by(name=COMPANY_NAME)
    building_uuids = select(BuildingDB.uuid).where(BuildingDB.company_uuid.in_(company_uuids))
    async with async_session_maker() as session:
        async with session.begin():
            await session.execute(delete(DeviceDB).where(DeviceDB.building_uuid.in_(building_uuids)))
            await session.execute(delete(BuildingDB).where(BuildingDB.company_uuid.in_(company_uuids)))
            await session.execute(delete(CompanyDB).filter_by(name=COMPANY_NAME))
    output.unlink(missing_ok=True)


def main() -> None:
    """Clear DB and keys for load test devices."""
    asyncio.run(remove_load_devices(DEFAULT_OUTPUT))


if __name__ == '__main__':
    main()
