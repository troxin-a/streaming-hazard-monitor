from enum import StrEnum


class UserRole(StrEnum):
    """User role inside the company."""
    EMPLOYEE = 'employee'
    DIRECTOR = 'director'
