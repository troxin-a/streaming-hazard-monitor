from sqlite3 import IntegrityError
from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select

from api.auth.schemes import RegistrationRequestScheme
from api.auth.services.utils import HashPassword
from shared.base.sessions import BaseSession
from shared.base.utils import handle_error
from shared.user.models import UserDB


class UserSession(BaseSession):
    """User session."""

    async def create_user(self, data: RegistrationRequestScheme):
        """Create user."""
        async with self.session.begin():
            hashed_password = HashPassword.hash_password(data.password1)
            data.password1 = hashed_password
            data = data.model_dump()
            data.pop('password1')
            data.pop('password2')
            data['password'] = hashed_password

            new_user = UserDB(**data)
            self.session.add(new_user)
            try:
                await self.session.flush()
            except IntegrityError as err:
                handle_error(err)
            return new_user

    async def get_user_by_uuid(self, uuid: UUID) -> UserDB:
        """Get user by uuid."""
        async with self.session.begin():
            query = select(UserDB).filter_by(uuid=uuid)
            res = await self.session.scalar(query)
            return res

    async def get_users(self) -> Page[UserDB]:
        """Get all users."""
        async with self.session.begin():
            query = select(UserDB).order_by(UserDB.created_at.desc())
            a = await apaginate(self.session, query)
            return a
