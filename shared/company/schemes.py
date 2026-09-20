from uuid import UUID

from shared.base.schemes import BaseScheme


class CompanyScheme(BaseScheme):
    """Company scheme."""
    uuid: UUID
    name: str


class CompanyCreateScheme(BaseScheme):
    """Company create scheme."""
    name: str


class CompanyUpdateScheme(BaseScheme):
    """Company update scheme."""
    name: str | None = None
