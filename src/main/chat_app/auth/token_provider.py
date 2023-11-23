import base64
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List

import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError


@dataclass
class User:
    username: str
    authorities: List[str]


class TokenState(Enum):
    SUCCESS         = auto()
    MALFORMED       = auto()
    EXPIRED         = auto()
    ILLEGAL         = auto()


class TokenProvider:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self._SECRET_KEY = 'a2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbQ=='
            self._VALIDITY_SEC = 10
            self._KEY = base64.b64decode(self._SECRET_KEY)
            cls._init = True

    def _create_default_token(self, payload: dict, validity: datetime):
        payload['exp'] = validity
        token = jwt.encode(
            payload=payload,
            key=self._KEY,
            algorithm='HS512',
        )
        return token

    def create_token(self, user: User) -> str:
        payload = {
            'sub': user.username,
            'auth': ','.join(user.authorities)
        }
        now = datetime.now()
        validity = now + timedelta(seconds=self._VALIDITY_SEC)

        return self._create_default_token(payload, validity)

    def get_user(self, token: str) -> User:
        payload = jwt.decode(token, self._KEY, algorithms=['HS512'])
        user = User(
            username=payload['sub'],
            authorities=payload['auth'].split(',')
        )
        return user

    def validate_token(self, token: str) -> TokenState:
        try:
            jwt.decode(token, self._KEY, algorithms=['HS512'])
        except DecodeError or InvalidTokenError:
            return TokenState.MALFORMED
        except ExpiredSignatureError:
            return TokenState.EXPIRED
        except ValueError:
            return TokenState.ILLEGAL
        return TokenState.SUCCESS
