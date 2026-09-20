from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import delete, select
from starlette import status

from shared.base.sessions import BaseSession
from shared.company.models import CompanyDB
from shared.company.schemes import CompanyCreateScheme, CompanyUpdateScheme


class CompanySession(BaseSession):
    """Company session."""

    async def get_companies(self) -> Page[CompanyDB]:
        """Get all companies."""
        async with self.session.begin():
            query = select(CompanyDB).order_by(CompanyDB.created_at.desc())
            return await apaginate(self.session, query)

    async def get_company(self, uuid: UUID) -> CompanyDB:
        """Get company by uuid."""
        async with self.session.begin():
            return await self._get_company(uuid)

    async def create_company(self, data: CompanyCreateScheme) -> CompanyDB:
        """Create company."""
        async with self.session.begin():
            company = CompanyDB(**data.model_dump())
            self.session.add(company)
            await self.flush()
            return company

    async def update_company(self, uuid: UUID, data: CompanyUpdateScheme) -> CompanyDB:
        """Update company."""
        async with self.session.begin():
            company = await self._get_company(uuid)
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(company, field, value)
            await self.flush()
            return company

    async def delete_company(self, uuid: UUID) -> None:
        """Delete company."""
        async with self.session.begin():
            await self._get_company(uuid)
            await self.execute(delete(CompanyDB).filter_by(uuid=uuid))
            await self.flush()

    async def _get_company(self, uuid: UUID) -> CompanyDB:
        """Get company by uuid or raise not found."""
        company = await self.session.scalar(select(CompanyDB).filter_by(uuid=uuid))
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')
        return company
