from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from shared.base.schemes import BaseScheme


class ReadingCreateScheme(BaseScheme):
    """Reading create scheme."""
    value: Decimal = Field(max_digits=10, decimal_places=3)


class ReadingMessageScheme(BaseScheme):
    """Reading message scheme."""
    device_uuid: UUID
    value: Decimal
    received_at: datetime


class ReadingScheme(BaseScheme):
    """Reading scheme."""
    uuid: UUID
    device_uuid: UUID
    value: Decimal
    created_at: datetime
