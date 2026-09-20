from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import delete, select, update
from starlette import status

from shared.base.sessions import BaseSession
from shared.company.models import CompanyDB
from shared.company.schemes import CompanyCreateScheme, CompanyUpdateScheme
from shared.user.models import UserDB


class CompanySession(BaseSession):
    """Company session."""

    async def get_companies(self, user: UserDB) -> Page[CompanyDB]:
        """Get companies visible to the user."""
        async with self.session.begin():
            query = select(CompanyDB).order_by(CompanyDB.created_at.desc())
            if not user.is_superuser:
                query = query.where(CompanyDB.uuid == user.company_uuid)
            return await apaginate(self.session, query)

    async def create_company(self, data: CompanyCreateScheme) -> CompanyDB:
        """Create company."""
        async with self.session.begin():
            company = CompanyDB(**data.model_dump())
            self.session.add(company)
            await self.flush()
            return company

    async def get_company(self, uuid: UUID, user: UserDB) -> CompanyDB:
        """Get company by uuid."""
        async with self.session.begin():
            return await self._get_visible_company(uuid, user)

    async def update_company(self, uuid: UUID, data: CompanyUpdateScheme, user: UserDB) -> CompanyDB:
        """Update company."""
        async with self.session.begin():
            fields = data.model_dump(exclude_unset=True)
            if not fields:
                return await self._get_visible_company(uuid, user)

            query = update(CompanyDB).filter_by(uuid=uuid).values(**fields).returning(CompanyDB)
            if not user.is_superuser:
                query = query.where(CompanyDB.uuid == user.company_uuid)

            company = await self.scalar(query)
            if not company:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')
            return company

    async def delete_company(self, uuid: UUID) -> None:
        """Delete company."""
        async with self.session.begin():
            company_uuid = await self.scalar(delete(CompanyDB).filter_by(uuid=uuid).returning(CompanyDB.uuid))
            if not company_uuid:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')

    async def _get_visible_company(self, uuid: UUID, user: UserDB) -> CompanyDB:
        """Get company the user is allowed to see or raise not found."""
        query = select(CompanyDB).filter_by(uuid=uuid)
        if not user.is_superuser:
            query = query.where(CompanyDB.uuid == user.company_uuid)
        company = await self.session.scalar(query)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')
        return company
