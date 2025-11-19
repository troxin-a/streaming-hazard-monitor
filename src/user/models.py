from sqlalchemy.orm import Mapped

from src.base.models import BaseDBModel, mc


# if TYPE_CHECKING:
#     from src import RoleDB, PairDB, LocationDB, EventDB, EventResponsibleUserDB, ActDB, ActItemDB, StatusTaskDB


class UserDB(BaseDBModel):
    """User database model."""
    __tablename__ = 'users'

    username: Mapped[str] = mc(index=True, unique=True)
    name: Mapped[str] = mc(unique=False)
    password: Mapped[str]
