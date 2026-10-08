import argparse
import asyncio
import json
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared import BuildingDB, CompanyDB, DeviceDB
from shared.config.session import async_session_maker
from shared.config.settings import BASE_DIR
from shared.device.enums import DeviceType
from shared.device.services import generate_api_key, hash_api_key

COMPANY_NAME = 'Test_company'
BUILDING_NAME = 'Test_building'
DEFAULT_COUNT = 1700
DEFAULT_OUTPUT = BASE_DIR / 'scripts' / 'k6-keys.json'


async def get_building_uuid(session: AsyncSession) -> UUID:
    """Return uuid of the load test building, creating it with its company if it is absent."""
    query = select(BuildingDB.uuid).filter_by(name=BUILDING_NAME)
    building_uuid = await session.scalar(query)
    if building_uuid is not None:
        return building_uuid
    company = CompanyDB(name=COMPANY_NAME)
    session.add(company)
    await session.flush()
    building = BuildingDB(company_uuid=company.uuid, name=BUILDING_NAME)
    session.add(building)
    await session.flush()
    return building.uuid


async def issue_api_keys(session: AsyncSession, building_uuid: UUID, count: int) -> list[str]:
    """Issue api keys to count load test devices of the building, creating the missing devices."""
    query = (
        select(DeviceDB)
        .where(DeviceDB.building_uuid == building_uuid, DeviceDB.serial_number.startswith('LOAD-'))
        .order_by(DeviceDB.serial_number)
        .limit(count)
    )
    devices = list(await session.scalars(query))
    devices += [
        DeviceDB(
            building_uuid=building_uuid,
            name=f'Device_{number}',
            serial_number=f'{'LOAD-'}{number:05d}',
            type=DeviceType.CO,
        )
        for number in range(len(devices) + 1, count + 1)
    ]
    keys = [generate_api_key() for _ in devices]
    for device, key in zip(devices, keys, strict=True):
        device.key_hash = hash_api_key(key)
    session.add_all(devices)
    return keys


async def create_load_devices(count: int, output: Path) -> None:
    """Prepare count load test devices and write their api keys to the output file."""
    async with async_session_maker() as session, session.begin():
        building_uuid = await get_building_uuid(session)
        keys = await issue_api_keys(session, building_uuid, count)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(keys))


def main() -> None:
    """Parse command line arguments and prepare the load test devices."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, default=DEFAULT_COUNT, help='Count of devices to create')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT, help='File to write device keys to')
    args = parser.parse_args()
    asyncio.run(create_load_devices(args.count, args.output))


if __name__ == '__main__':
    main()
