from decimal import Decimal
from operator import attrgetter
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import (
    and_, case, ColumnElement, delete, insert, literal_column, or_, Row, select, Select, true, update, Update,
)
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import coalesce
from starlette import status

from shared.base.sessions import BaseSession
from shared.building.models import BuildingDB
from shared.device.enums import AlertLevel
from shared.device.models import DefaultThresholdDB, DeviceDB, DeviceThresholdDB
from shared.device.schemes import DeviceCreateScheme, DeviceUpdateScheme, ThresholdsSetScheme
from shared.device.services import generate_api_key, hash_api_key
from shared.user.enums import UserRole
from shared.user.models import UserDB

PREVIOUS_KEY_HASH = literal_column('old.key_hash').label('previous_key_hash')


class DeviceSession(BaseSession):
    """Device session."""

    async def get_devices(self, user: UserDB, search: str | None = None) -> Page[DeviceDB]:
        """Get devices visible to the user, optionally narrowed by a part of the name or the serial number."""
        async with self.session.begin():
            query = select(DeviceDB).where(self._visible(user)).order_by(DeviceDB.created_at.desc())
            if search:
                pattern = f'%{search}%'
                query = query.where(or_(DeviceDB.name.ilike(pattern), DeviceDB.serial_number.ilike(pattern)))
            query = query.options(joinedload(DeviceDB.building).joinedload(BuildingDB.company))
            return await apaginate(self.session, query)

    async def create_device(self, data: DeviceCreateScheme, user: UserDB) -> DeviceDB:
        """Create device."""
        async with self.session.begin():
            building = await self._get_visible_building(data.building_uuid, user)
            device = DeviceDB(**data.model_dump(exclude={'building_uuid'}), building=building)
            self.session.add(device)
            await self.flush()
            return device

    async def get_device(self, uuid: UUID, user: UserDB) -> DeviceDB:
        """Get device by uuid."""
        async with self.session.begin():
            return await self._get_visible_device(uuid, user)

    async def update_device(self, uuid: UUID, data: DeviceUpdateScheme, user: UserDB) -> DeviceDB:
        """Update device."""
        async with self.session.begin():
            fields = data.model_dump(exclude_unset=True)
            if not fields:
                return await self._get_visible_device(uuid, user)
            if fields.get('building_uuid'):
                await self._get_visible_building(fields['building_uuid'], user)

            query = update(DeviceDB).where(DeviceDB.uuid == uuid, self._visible(user)).values(**fields)
            device = await self.scalar(query.returning(DeviceDB))
            if not device:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Device not found')
            return device

    async def delete_device(self, uuid: UUID, user: UserDB) -> None:
        """Delete device."""
        async with self.session.begin():
            query = delete(DeviceDB).where(DeviceDB.uuid == uuid, self._visible(user))
            device_uuid = await self.scalar(query.returning(DeviceDB.uuid))
            if not device_uuid:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Device not found')

    async def create_api_key(self, uuid: UUID, user: UserDB) -> str:
        """Issue an api key for the device and return it in plain text."""
        async with self.session.begin():
            key = generate_api_key()
            query = (
                update(DeviceDB)
                .where(DeviceDB.uuid == uuid, self._visible(user))
                .values(key_hash=coalesce(DeviceDB.key_hash, hash_api_key(key)))
                .returning(PREVIOUS_KEY_HASH)
            )
            previous = await self._previous_key_hash(query)
            if previous is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Device already has an api key')
            return key

    async def delete_api_key(self, uuid: UUID, user: UserDB) -> None:
        """Revoke the api key of the device."""
        async with self.session.begin():
            query = (
                update(DeviceDB)
                .where(DeviceDB.uuid == uuid, self._visible(user))
                .values(key_hash=None)
                .returning(PREVIOUS_KEY_HASH)
            )
            previous = await self._previous_key_hash(query)
            if previous is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Device has no api key')

    async def _previous_key_hash(self, query: Update) -> str | None:
        """Return the api key hash stored before the update or raise not found."""
        row = (await self.execute(query)).one_or_none()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Device not found')
        return row.previous_key_hash

    @staticmethod
    def _visible(user: UserDB) -> ColumnElement[bool]:
        """Build the condition limiting devices to the ones the user is allowed to see."""
        if user.is_superuser:
            return true()
        if user.role == UserRole.DIRECTOR:
            company_buildings = select(BuildingDB.uuid).where(BuildingDB.company_uuid == user.company_uuid)
            return DeviceDB.building_uuid.in_(company_buildings)
        return DeviceDB.building_uuid == user.building_uuid

    async def _get_visible_device(self, uuid: UUID, user: UserDB) -> DeviceDB:
        """Get device the user is allowed to see or raise not found."""
        query = (
            select(DeviceDB)
            .where(DeviceDB.uuid == uuid, self._visible(user))
            .options(joinedload(DeviceDB.building).joinedload(BuildingDB.company))
        )
        device = await self.session.scalar(query)
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Device not found')
        return device

    async def _get_visible_building(self, uuid: UUID, user: UserDB) -> BuildingDB:
        """Get building the user is allowed to see or raise not found."""
        query = select(BuildingDB).filter_by(uuid=uuid)
        if not user.is_superuser:
            query = query.where(BuildingDB.company_uuid == user.company_uuid)
        building = await self.session.scalar(query.options(joinedload(BuildingDB.company)))
        if not building:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Building not found')
        return building


class ThresholdSession(DeviceSession):
    """Device threshold session."""

    async def get_thresholds(
            self,
            device_uuid: UUID,
            user: UserDB,
    ) -> Sequence[Row[tuple[AlertLevel, Decimal, bool]]]:
        """Get thresholds set for the device or the default ones of its type."""
        async with self.session.begin():
            own, default = DeviceThresholdDB, DefaultThresholdDB
            query = (
                select(
                    coalesce(own.level, default.level).label('level'),
                    coalesce(own.value, default.value).label('value'),
                    own.uuid.is_(None).label('is_default'),
                )
                .select_from(DeviceDB)
                .outerjoin(own, own.device_uuid == DeviceDB.uuid)
                .outerjoin(default, and_(default.device_type == DeviceDB.type, own.uuid.is_(None)))
                .where(DeviceDB.uuid == device_uuid, self._visible(user))
                .order_by('level')
            )
            rows = (await self.session.execute(query)).all()
            if not rows:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Device not found')
            return [row for row in rows if row.level is not None]

    async def create_thresholds(
            self,
            device_uuid: UUID,
            data: ThresholdsSetScheme,
            user: UserDB,
    ) -> list[DeviceThresholdDB]:
        """Set thresholds of every level for the device."""
        async with self.session.begin():
            await self._get_visible_device(device_uuid, user)
            rows = [
                {'device_uuid': device_uuid, 'level': level, 'value': value}
                for level, value in data.by_level().items()
            ]
            query = insert(DeviceThresholdDB).values(rows).returning(DeviceThresholdDB)
            thresholds = (await self.execute(query)).scalars().all()
            return sorted(thresholds, key=attrgetter('level'))

    async def update_thresholds(
            self,
            device_uuid: UUID,
            data: ThresholdsSetScheme,
            user: UserDB,
    ) -> list[DeviceThresholdDB]:
        """Update thresholds of every level set for the device."""
        async with self.session.begin():
            query = (
                update(DeviceThresholdDB)
                .where(
                    DeviceThresholdDB.device_uuid == device_uuid,
                    DeviceThresholdDB.device_uuid.in_(self._visible_devices(user)),
                )
                .values(value=case(data.by_level(), value=DeviceThresholdDB.level))
                .returning(DeviceThresholdDB)
            )
            thresholds = (await self.execute(query)).scalars().all()
            if not thresholds:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Thresholds not found')
            return sorted(thresholds, key=attrgetter('level'))

    async def delete_thresholds(self, device_uuid: UUID, user: UserDB) -> None:
        """Delete thresholds set for the device."""
        async with self.session.begin():
            query = delete(DeviceThresholdDB).where(
                DeviceThresholdDB.device_uuid == device_uuid,
                DeviceThresholdDB.device_uuid.in_(self._visible_devices(user)),
            )
            deleted = (await self.execute(query.returning(DeviceThresholdDB.uuid))).all()
            if not deleted:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Thresholds not found')

    def _visible_devices(self, user: UserDB) -> Select[tuple[UUID]]:
        """Build the query of the uuids of the devices the user is allowed to see."""
        return select(DeviceDB.uuid).where(self._visible(user))
