from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import ColumnElement, select, true
from sqlalchemy.orm import joinedload

from shared.alert.models import AlertDB
from shared.base.sessions import BaseSession
from shared.building.models import BuildingDB
from shared.user.enums import UserRole
from shared.user.models import UserDB


class AlertSession(BaseSession):
    """Alert session."""

    async def get_alerts(self, user: UserDB) -> Page[AlertDB]:
        """Get alerts in progress visible to the user, the most dangerous and then the latest first."""
        async with self.session.begin():
            query = (
                select(AlertDB)
                .where(AlertDB.ended_at.is_(None), self._visible_alerts(user))
                .order_by(AlertDB.level.desc(), AlertDB.started_at.desc(), AlertDB.uuid)
                .options(joinedload(AlertDB.device), joinedload(AlertDB.building))
            )
            return await apaginate(self.session, query)

    @staticmethod
    def _visible_alerts(user: UserDB) -> ColumnElement[bool]:
        """Build the condition limiting alerts to the ones the user is allowed to see."""
        if user.is_superuser:
            return true()
        if user.role == UserRole.DIRECTOR:
            company_buildings = select(BuildingDB.uuid).where(BuildingDB.company_uuid == user.company_uuid)
            return AlertDB.building_uuid.in_(company_buildings)
        return AlertDB.building_uuid == user.building_uuid
