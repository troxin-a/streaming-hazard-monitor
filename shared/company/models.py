from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from shared.base.models import BaseDBModel, mc

if TYPE_CHECKING:
    from shared.building.models import BuildingDB


class CompanyDB(BaseDBModel):
    """Company database model."""
    __tablename__ = 'companies'

    name: Mapped[str] = mc(index=True)

    buildings: Mapped[list['BuildingDB']] = relationship(back_populates='company')
