import base64
import hashlib
import hmac

import jwt

from fastapi import HTTPException

from socketio import AsyncNamespace
from starlette import status

SECRET_KEY = 'a2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbQ=='


# 인증 함수: JWT를 검증하고 클라이언트를 식별합니다.
def authenticate(token) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"Authenticate": "Bearer"},
    )

    try:
        key = base64.b64decode(SECRET_KEY)

        payload = jwt.decode(token, key, algorithms=['HS512'])
        username = payload.get("sub")
        if username is None:
            return None
    except jwt.PyJWTError:
        return None

    return username


class ChatNamespace(AsyncNamespace):
    def __init__(self, namespace):
        super().__init__(namespace=namespace)
        self.name = namespace
        self.authenticated_sids = set()
        self.user_info = dict()
        # redis 채팅 방 생성

    async def on_connect(self, sid, environ):
        authorization = environ.get("HTTP_AUTHORIZATION")

        username = None
        if authorization:
            token = authorization[7:]
            username = authenticate(token)

        if username:
            self.authenticated_sids.add(sid)
            self.user_info[sid] = username
            await self.emit("message", {"message": f"User {username} connected"})
        else:
            print(f"Invalid token. Allowing connection: {sid}")

    async def on_disconnect(self, sid):
        print(f"Client disconnected: {sid}")
        if sid in self.authenticated_sids:
            self.authenticated_sids.discard(sid)
            del self.user_info[sid]

    async def on_message(self, sid, data):
        # redis 채팅 등록
        if sid in self.authenticated_sids:
            username = self.user_info[sid]
            await self.emit("message", {"message": f"Message from {username}({sid}): {data}"})
            print(f"Message from {username}({sid}): {data}")
        else:
            print(f"Ignoring message from unauthenticated client {sid}")