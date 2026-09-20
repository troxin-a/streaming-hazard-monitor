from typing import Any
from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import delete, Select, select, update
from sqlalchemy.orm import selectinload
from starlette import status

from api.auth.services.utils import HashPassword
from shared.base.sessions import BaseSession
from shared.building.models import BuildingDB
from shared.company.models import CompanyDB
from shared.user.enums import UserRole
from shared.user.models import UserDB
from shared.user.schemes import UserCreateScheme, UserUpdateScheme


class UserSession(BaseSession):
    """User session."""

    async def get_users(self, author: UserDB) -> Page[UserDB]:
        """Get users visible to the author."""
        async with self.session.begin():
            query = self._visible_users(select(UserDB), author).order_by(UserDB.created_at.desc())
            return await apaginate(self.session, query)

    async def create_user(self, data: UserCreateScheme, author: UserDB) -> UserDB:
        """Create user by superuser or by the director of their company."""
        async with self.session.begin():
            company_uuid = self._get_company_uuid(data, author)
            await self._check_company(company_uuid)
            await self._check_building(data.building_uuid, company_uuid)

            user_data = data.model_dump(exclude={'password1', 'password2', 'company_uuid'})
            user_data['password'] = HashPassword.hash_password(data.password1)

            new_user = UserDB(company_uuid=company_uuid, **user_data)
            self.session.add(new_user)
            await self.flush()
            return new_user

    async def get_user(self, uuid: UUID, author: UserDB) -> UserDB:
        """Get user with its building and company by uuid or raise not found."""
        async with self.session.begin():
            query = select(UserDB).options(selectinload(UserDB.building)).filter_by(uuid=uuid)
            user = await self.session.scalar(self._visible_users(query, author))
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
            return user

    async def get_user_by_uuid(self, uuid: UUID) -> UserDB:
        """Get user by uuid."""
        async with self.session.begin():
            query = select(UserDB).filter_by(uuid=uuid)
            res = await self.session.scalar(query)
            return res

    async def update_user(self, uuid: UUID, data: UserUpdateScheme, author: UserDB) -> UserDB:
        """Update user by themselves, by the director of their company or by superuser."""
        async with self.session.begin():
            user = await self._get_visible_user(uuid, author)
            fields = self._get_update_fields(data, user, author)
            if not fields:
                return user

            if 'company_uuid' in fields or 'building_uuid' in fields:
                company_uuid = fields.get('company_uuid') or user.company_uuid
                if 'company_uuid' in fields:
                    await self._check_company(company_uuid)
                await self._check_building(fields.get('building_uuid') or user.building_uuid, company_uuid)

            return await self.scalar(update(UserDB).filter_by(uuid=uuid).values(**fields).returning(UserDB))

    async def delete_user(self, uuid: UUID, author: UserDB) -> None:
        """Delete user of the author company."""
        async with self.session.begin():
            if uuid == author.uuid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Cannot delete yourself')

            query = delete(UserDB).filter_by(uuid=uuid).returning(UserDB.uuid)
            if not author.is_superuser:
                query = query.where(UserDB.company_uuid == author.company_uuid)

            user_uuid = await self.scalar(query)
            if not user_uuid:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    @staticmethod
    def _get_company_uuid(data: UserCreateScheme, author: UserDB) -> UUID:
        """Get the company of the created user or raise forbidden."""
        if author.is_superuser:
            if not data.company_uuid:
                detail = [{'field': 'company_uuid', 'message': 'Company is required'}]
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail)
            return data.company_uuid
        if author.role == UserRole.DIRECTOR and data.role == UserRole.EMPLOYEE:
            return author.company_uuid
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')

    @staticmethod
    def _get_update_fields(data: UserUpdateScheme, user: UserDB, author: UserDB) -> dict[str, Any]:
        """Get fields the author may change on the user or raise forbidden."""
        fields = data.model_dump(exclude_unset=True, exclude={'password1', 'password2'})
        if data.password1:
            fields['password'] = HashPassword.hash_password(data.password1)
        if author.is_superuser:
            return fields

        if author.role != UserRole.DIRECTOR and user.uuid != author.uuid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')

        forbidden = {'role', 'company_uuid'}
        if author.role != UserRole.DIRECTOR:
            forbidden.add('building_uuid')
        if forbidden & fields.keys():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')
        return fields

    @staticmethod
    def _visible_users(query: Select, author: UserDB) -> Select:
        """Narrow the query to users the author is allowed to see."""
        if author.is_superuser:
            return query
        if author.role == UserRole.DIRECTOR:
            return query.where(UserDB.company_uuid == author.company_uuid)
        if author.role == UserRole.EMPLOYEE and author.building_uuid:
            return query.where(UserDB.building_uuid == author.building_uuid)
        return query.where(UserDB.uuid == author.uuid)

    async def _get_visible_user(self, uuid: UUID, author: UserDB) -> UserDB:
        """Get user the author is allowed to see or raise not found."""
        user = await self.session.scalar(self._visible_users(select(UserDB).filter_by(uuid=uuid), author))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        return user

    async def _check_company(self, uuid: UUID) -> None:
        """Check the company exists or raise not found."""
        company = await self.session.scalar(select(CompanyDB).filter_by(uuid=uuid))
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')

    async def _check_building(self, uuid: UUID | None, company_uuid: UUID) -> None:
        """Check the building belongs to the company or raise not found."""
        if not uuid:
            return
        building = await self.session.scalar(select(BuildingDB).filter_by(uuid=uuid, company_uuid=company_uuid))
        if not building:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Building not found')
