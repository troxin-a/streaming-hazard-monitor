from uuid import UUID

from shared.base.schemes import BaseScheme
from shared.building.schemes import BuildingScheme


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
