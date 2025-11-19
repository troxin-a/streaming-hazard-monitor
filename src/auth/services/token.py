import datetime
from typing import Tuple

import jwt
from fastapi import HTTPException
from starlette import status

from src.config.settings import config
from src.user.models import UserDB


class Token:
    """Token."""
    token_type: str = 'access'
    expire_token_min: int = 10
    key: str = 'SECRET_KEY'
    algorithm = 'HS256'

    def __init__(self, token: str = None):
        self.jwt_token = token

    @classmethod
    def for_user(cls, user: UserDB, sub: str = None, expires_delta_min: int = None, remember_me: bool = False) -> str:
        """Get token for user."""
        now = datetime.datetime.now()
        if expires_delta_min:
            expire = now + datetime.timedelta(minutes=expires_delta_min)
        else:
            expire = now + datetime.timedelta(minutes=cls.expire_token_min)
        if remember_me:
            expire = now + datetime.timedelta(minutes=config.jwt.REFRESH_TOKEN_EXPIRE_MINUTES_REMEMBER)
        payload = {
            'token_type': cls.token_type,
            'exp': expire,
            'user_uuid': f'{user.uuid}',
            'remember_me': remember_me,
        }
        if sub:
            payload['sub'] = sub
        token = jwt.encode(payload=payload, key=cls.key, algorithm=cls.algorithm)
        return token

    @property
    def payload(self) -> dict:
        """Get payload."""
        try:
            payload = jwt.decode(self.jwt_token, key=self.key, algorithms=[self.algorithm])
            return payload
        except jwt.exceptions.InvalidSignatureError:
            message_error = 'Token invalid signature error'
        except jwt.exceptions.DecodeError:
            message_error = 'Token decode error'
        except jwt.exceptions.ExpiredSignatureError:
            message_error = 'Token expired signature error'
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message_error)


class AccessToken(Token):
    """Access Token."""
    expire_token_min = config.jwt.ACCESS_TOKEN_EXPIRE_MINUTES
    key = config.jwt.SECRET_KEY


class RefreshToken(Token):
    """Refresh Token."""
    token_type = 'refresh'
    expire_token_min = config.jwt.REFRESH_TOKEN_EXPIRE_MINUTES
    key = config.jwt.SECRET_KEY

    def update_tokens(self, payload: dict) -> Tuple[str, str]:
        """Update tokens."""
        token_type = payload.get('token_type')
        if token_type == self.token_type:
            now = datetime.datetime.now()
            expire = now + datetime.timedelta(minutes=self.expire_token_min)
            payload['exp'] = expire
            remember_me = payload.get('remember_me', False)
            if remember_me:
                payload['exp'] = now + datetime.timedelta(minutes=config.jwt.REFRESH_TOKEN_EXPIRE_MINUTES_REMEMBER)
            refresh_token = jwt.encode(payload=payload, key=self.key, algorithm=self.algorithm)
            expire_access = now + datetime.timedelta(minutes=AccessToken.expire_token_min)
            payload['exp'] = expire_access
            payload['token_type'] = 'access'
            access_token = jwt.encode(payload=payload, key=self.key, algorithm=self.algorithm)
            return access_token, refresh_token
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token invalid type')
