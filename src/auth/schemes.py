from typing import Any

from fastapi import HTTPException
from pydantic import model_validator
from starlette import status

from src.base.schemes import BaseScheme


class RegistrationRequestScheme(BaseScheme):
    """Registration request Scheme."""
    username: str
    name: str
    password1: str
    password2: str

    @model_validator(mode='before')
    @classmethod
    def password_validator(cls, data: Any) -> Any:
        """Validate the password field."""
        if isinstance(data, dict):
            if data['password1'] != data['password2']:
                detail = [{
                    'field': 'password1',
                    'message': 'Passwords must be the same',
                }]
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail)
        return data


class RegistrationResponseScheme(BaseScheme):
    """Registration response Scheme."""
    username: str
    name: str


class LoginResponseScheme(BaseScheme):
    """Login Response Scheme."""
    access: str
    refresh: str

    model_config = {
        'json_schema_extra': {
            'examples': [{
                'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....',
                'refresh': 'tg7HJKHG6GKfI1NiIsInR5cCI6IkpHjkgY....',
            }],
        }
    }


class LoginScheme(BaseScheme):
    """Login Scheme."""
    username: str
    password: str
    remember_me: bool = False


class RefreshScheme(BaseScheme):
    """Refresh Token Scheme."""
    refresh: str

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'refresh': 'tg7HJKHG6GKfI1NiIsInR5cCI6IkpHjkgY....',
                },
            ],
        }
    }
