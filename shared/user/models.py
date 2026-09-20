from typing import TYPE_CHECKING

from sqlalchemy import false, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.base.models import BaseDBModel, FK, mc

if TYPE_CHECKING:
    from shared.building.models import BuildingDB


class UserDB(BaseDBModel):
    """User database model."""
    __tablename__ = 'users'

    username: Mapped[str] = mc(index=True, unique=True)
    name: Mapped[str] = mc(unique=False)
    password: Mapped[str]
    is_superuser: Mapped[bool] = mc(default=False, server_default=false())
    building_uuid: Mapped[UUID | None] = mc(UUID(), FK('buildings.uuid'), index=True, nullable=True)

    building: Mapped['BuildingDB | None'] = relationship(back_populates='users')
