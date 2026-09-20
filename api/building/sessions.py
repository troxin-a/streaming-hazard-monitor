from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import delete, Select, select, update
from starlette import status

from shared.base.sessions import BaseSession
from shared.building.models import BuildingDB
from shared.building.schemes import BuildingCreateScheme, BuildingUpdateScheme
from shared.company.models import CompanyDB
from shared.user.enums import UserRole
from shared.user.models import UserDB


class BuildingSession(BaseSession):
    """Building session."""

    async def get_buildings(self, user: UserDB) -> Page[BuildingDB]:
        """Get buildings visible to the user."""
        async with self.session.begin():
            query = self._visible_buildings(select(BuildingDB), user).order_by(BuildingDB.created_at.desc())
            return await apaginate(self.session, query)

    async def create_building(self, data: BuildingCreateScheme, user: UserDB) -> BuildingDB:
        """Create building."""
        async with self.session.begin():
            await self._check_company(data.company_uuid, user)
            building = BuildingDB(**data.model_dump())
            self.session.add(building)
            await self.flush()
            await self.session.refresh(building)
            return building

    async def get_building(self, uuid: UUID, user: UserDB) -> BuildingDB:
        """Get building by uuid."""
        async with self.session.begin():
            return await self._get_visible_building(uuid, user)

    async def update_building(self, uuid: UUID, data: BuildingUpdateScheme, user: UserDB) -> BuildingDB:
        """Update building."""
        async with self.session.begin():
            fields = data.model_dump(exclude_unset=True)
            if not fields:
                return await self._get_visible_building(uuid, user)
            if fields.get('company_uuid'):
                await self._check_company(fields['company_uuid'], user)

            query = update(BuildingDB).filter_by(uuid=uuid).values(**fields).returning(BuildingDB)
            if not user.is_superuser:
                query = query.where(BuildingDB.company_uuid == user.company_uuid)

            building = await self.scalar(query)
            if not building:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Building not found')
            return building

    async def delete_building(self, uuid: UUID, user: UserDB) -> None:
        """Delete building."""
        async with self.session.begin():
            query = delete(BuildingDB).filter_by(uuid=uuid).returning(BuildingDB.uuid)
            if not user.is_superuser:
                query = query.where(BuildingDB.company_uuid == user.company_uuid)

            building_uuid = await self.scalar(query)
            if not building_uuid:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Building not found')

    @staticmethod
    def _visible_buildings(query: Select, user: UserDB) -> Select:
        """Narrow the query to buildings the user is allowed to see."""
        if user.is_superuser:
            return query
        if user.role == UserRole.DIRECTOR:
            return query.where(BuildingDB.company_uuid == user.company_uuid)
        return query.where(BuildingDB.uuid == user.building_uuid)

    async def _get_visible_building(self, uuid: UUID, user: UserDB) -> BuildingDB:
        """Get building the user is allowed to see or raise not found."""
        building = await self.session.scalar(self._visible_buildings(select(BuildingDB).filter_by(uuid=uuid), user))
        if not building:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Building not found')
        return building

    async def _check_company(self, uuid: UUID, user: UserDB) -> None:
        """Check the company is visible to the user or raise not found."""
        query = select(CompanyDB).filter_by(uuid=uuid)
        if not user.is_superuser:
            query = query.where(CompanyDB.uuid == user.company_uuid)
        company = await self.session.scalar(query)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')
