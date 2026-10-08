import asyncio
from pathlib import Path

from sqlalchemy.sql.expression import delete

from scripts.create_load_devices import COMPANY_NAME, DEFAULT_OUTPUT
from shared import CompanyDB
from shared.config.session import async_session_maker


async def remove_load_devices(output: Path) -> None:
    """Prepare count load test devices and write their api keys to the output file."""
    async with async_session_maker() as session:
        async with session.begin():
            await session.execute(delete(CompanyDB).filter_by(name=COMPANY_NAME))
    output.unlink(missing_ok=True)


def main() -> None:
    """Clear DB and keys for load test devices."""
    asyncio.run(remove_load_devices(DEFAULT_OUTPUT))


if __name__ == '__main__':
    main()
