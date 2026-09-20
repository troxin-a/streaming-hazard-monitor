from typing import Any
from uuid import UUID

from fastapi import HTTPException
from pydantic import model_validator
from starlette import status

from shared.base.schemes import BaseScheme
from shared.building.schemes import BuildingScheme
from shared.user.enums import UserRole


class UserListScheme(BaseScheme):
    """User list scheme."""
    uuid: UUID
    name: str


class UserScheme(BaseScheme):
    """User scheme."""
    uuid: UUID
    name: str
    is_superuser: bool
    building: BuildingScheme | None


class UserCreateScheme(BaseScheme):
    """User create scheme."""
    username: str
    name: str
    role: UserRole
    password1: str
    password2: str
    company_uuid: UUID | None = None
    building_uuid: UUID | None = None

    @model_validator(mode='before')
    @classmethod
    def password_validator(cls, data: Any) -> Any:
        """Validate the password field."""
        if isinstance(data, dict):
            if data.get('password1') != data.get('password2'):
                detail = [{
                    'field': 'password1',
                    'message': 'Passwords must be the same',
                }]
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail)
        return data

    @model_validator(mode='after')
    def building_validator(self) -> 'UserCreateScheme':
        """Validate the building field."""
        if self.role == UserRole.EMPLOYEE and not self.building_uuid:
            detail = [{
                'field': 'building_uuid',
                'message': 'Building is required for an employee',
            }]
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail)
        return self


class UserUpdateScheme(BaseScheme):
    """User update scheme."""
    name: str | None = None
    password1: str | None = None
    password2: str | None = None
    role: UserRole | None = None
    company_uuid: UUID | None = None
    building_uuid: UUID | None = None

    @model_validator(mode='after')
    def password_validator(self) -> 'UserUpdateScheme':
        """Validate the password fields."""
        if (self.password1 or self.password2) and self.password1 != self.password2:
            detail = [{
                'field': 'password1',
                'message': 'Passwords must be the same',
            }]
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail)
        return self


class UserSavedScheme(BaseScheme):
    """Saved user scheme."""
    uuid: UUID
    username: str
    name: str
    role: UserRole
    company_uuid: UUID
    building_uuid: UUID | None
