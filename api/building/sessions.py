from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import delete, select
from starlette import status

from shared.base.sessions import BaseSession
from shared.building.models import BuildingDB
from shared.building.schemes import BuildingCreateScheme, BuildingUpdateScheme


class BuildingSession(BaseSession):
    """Building session."""

    async def get_buildings(self) -> Page[BuildingDB]:
        """Get all buildings."""
        async with self.session.begin():
            query = select(BuildingDB).order_by(BuildingDB.created_at.desc())
            return await apaginate(self.session, query)

    async def get_building(self, uuid: UUID) -> BuildingDB:
        """Get building by uuid."""
        async with self.session.begin():
            return await self._get_building(uuid)

    async def create_building(self, data: BuildingCreateScheme) -> BuildingDB:
        """Create building."""
        async with self.session.begin():
            building = BuildingDB(**data.model_dump())
            self.session.add(building)
            await self.flush()
            await self.session.refresh(building)
            return building

    async def update_building(self, uuid: UUID, data: BuildingUpdateScheme) -> BuildingDB:
        """Update building."""
        async with self.session.begin():
            building = await self._get_building(uuid)
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(building, field, value)
            await self.flush()
            await self.session.refresh(building)
            return building

    async def delete_building(self, uuid: UUID) -> None:
        """Delete building."""
        async with self.session.begin():
            await self._get_building(uuid)
            await self.execute(delete(BuildingDB).filter_by(uuid=uuid))
            await self.flush()

    async def _get_building(self, uuid: UUID) -> BuildingDB:
        """Get building by uuid or raise not found."""
        building = await self.session.scalar(select(BuildingDB).filter_by(uuid=uuid))
        if not building:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Building not found')
        return building
