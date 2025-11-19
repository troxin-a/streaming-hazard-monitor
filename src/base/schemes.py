from datetime import datetime

from pydantic import BaseModel, field_serializer


class ExceptionScheme(BaseModel):
    """Base Exception Scheme."""
    detail: str


class ExceptionValidationFieldScheme(BaseModel):
    """Exception Validation Field Scheme."""
    field: str = 'field name'
    message: str = 'message error'


class ExceptionValidationScheme(BaseModel):
    """Base Exception Validation Scheme."""
    detail: list[ExceptionValidationFieldScheme]


class BaseScheme(BaseModel):
    """Base Scheme."""

    @field_serializer('create_date', 'update_date', check_fields=False)
    def custom_datetime_format(self, dt: datetime):
        """Custom datetime format."""
        return datetime.strftime(dt, "%Y-%m-%d, %H:%M:%S")
