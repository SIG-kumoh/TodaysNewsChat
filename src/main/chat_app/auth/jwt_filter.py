from typing import Union, List, Dict, Optional

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from .token_provider import TokenProvider, TokenState, User
from chat_app.redis.redis_service import RedisService


class JWTFilter(HTTPBearer):
    def __init__(
            self,
            allow_role: Union[str, List[str]] = None,
            auto_error: bool = True,
    ):
        super().__init__(auto_error=auto_error)
        self._tp = TokenProvider()
        self._rs = RedisService()

        if isinstance(allow_role, str):
            self._allow_role = [allow_role]

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        http_credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if http_credentials:
            jwt = http_credentials.credentials
            token_state: TokenState = self._tp.validate_token(jwt)

            if self._rs.exists_access_token_in_redis(jwt):
                http_credentials.credentials = ''

            elif token_state == TokenState.EXPIRED:
                cookies = request.cookies
                http_credentials.credentials = await self.token_refresh(cookies)

        try:
            user = self._tp.get_user(http_credentials.credentials)
        except:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="HTTP_401_UNAUTHORIZED")
        if user and self._allow_role and not await self.has_role(user):
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="HTTP_403_FORBIDDEN")

        return http_credentials

    async def token_refresh(self, cookies: Dict[str, str]) -> str:
        jwt = None
        if 'refresh-token' in cookies:
            refresh_token = cookies['refresh-token']
            if self._tp.validate_token(refresh_token) != TokenState.SUCCESS:
                return None
            user = self._tp.get_user(refresh_token)

            if self._rs.get_refresh_token_by_redis(username=user.username) == refresh_token.encode():
                jwt = self._tp.create_token(user=user)

        return jwt

    async def has_role(self, user: User) -> bool:
        for role in self._allow_role:
            if role in user.authorities:
                return True
        return False
