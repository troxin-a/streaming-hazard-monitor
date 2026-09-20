from typing import TYPE_CHECKING

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, relationship

from shared.base.models import BaseDBModel, FK, mc

if TYPE_CHECKING:
    from shared.company.models import CompanyDB
    from shared.user.models import UserDB


class BuildingDB(BaseDBModel):
    """Building database model."""
    __tablename__ = 'buildings'

    name: Mapped[str] = mc(index=True)
    company_uuid: Mapped[UUID] = mc(UUID(), FK('companies.uuid'), index=True)

    company: Mapped['CompanyDB'] = relationship(back_populates='buildings', lazy='selectin')
    users: Mapped[list['UserDB']] = relationship(back_populates='building')
