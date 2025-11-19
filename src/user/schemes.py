from uuid import UUID

from src.base.schemes import BaseScheme


class UserListScheme(BaseScheme):
    """User list scheme."""
    uuid: UUID
    name: str
