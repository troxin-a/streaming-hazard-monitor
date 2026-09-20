from uuid import UUID

from shared.base.schemes import BaseScheme
from shared.company.schemes import CompanyScheme


class BuildingScheme(BaseScheme):
    """Building scheme."""
    uuid: UUID
    name: str
    company: CompanyScheme


class BuildingCreateScheme(BaseScheme):
    """Building create scheme."""
    name: str
    company_uuid: UUID


class BuildingUpdateScheme(BaseScheme):
    """Building update scheme."""
    name: str | None = None
    company_uuid: UUID | None = None
