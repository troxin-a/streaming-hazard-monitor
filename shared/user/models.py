from typing import TYPE_CHECKING

from sqlalchemy import Enum, false, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.base.models import BaseDBModel, FK, mc
from shared.user.enums import UserRole

if TYPE_CHECKING:
    from shared.building.models import BuildingDB
    from shared.company.models import CompanyDB


class UserDB(BaseDBModel):
    """User database model."""
    __tablename__ = 'users'

    username: Mapped[str] = mc(index=True, unique=True)
    name: Mapped[str] = mc(unique=False)
    password: Mapped[str]
    is_superuser: Mapped[bool] = mc(default=False, server_default=false())
    role: Mapped[UserRole] = mc(
        Enum(UserRole, name='user_role', values_callable=lambda roles: [role.value for role in roles]),
        default=UserRole.EMPLOYEE,
        server_default=UserRole.EMPLOYEE.value,
    )
    company_uuid: Mapped[UUID | None] = mc(UUID(), FK('companies.uuid'), index=True, nullable=True)
    building_uuid: Mapped[UUID | None] = mc(UUID(), FK('buildings.uuid'), index=True, nullable=True)

    company: Mapped['CompanyDB | None'] = relationship(back_populates='users')
    building: Mapped['BuildingDB | None'] = relationship(back_populates='users')
