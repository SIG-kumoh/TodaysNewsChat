import base64
from urllib.request import Request

import jwt
from fastapi.security import HTTPAuthorizationCredentials

from socketio import AsyncNamespace

from chat_app.auth import TokenProvider, TokenState, JWTFilter
from chat_app.redis.redis_service import RedisService

SECRET_KEY = 'a2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbXRva2FyaW10b2thcmltdG9rYXJpbQ=='


class ChatNamespace(AsyncNamespace):
    def __init__(self, namespace):
        super().__init__(namespace=namespace)
        self.name = namespace
        self.authenticated_sids = set()
        self.user_info = dict()
        self._rs = RedisService()
        self._tp = TokenProvider()
        self._filter = JWTFilter()

    async def on_connect(self, sid, environ):
        request = Request(
            'http://temp',
            headers={
                'Cookie': environ.get('HTTP_COOKIE'),
                'Authorization': environ.get('HTTP_AUTHORIZATION')
            }
        )
        try:
            http_credentials: HTTPAuthorizationCredentials = await self._filter(request)
            token = http_credentials.credentials
            user = self._tp.get_user(token)
            self.authenticated_sids.add(sid)
            self.user_info[sid] = user.username
            await self.emit("message", {"message": f"User {user.username} connected"})
        except:
            print(f"Invalid token. Allowing connection: {sid}")

    async def on_disconnect(self, sid):
        print(f"Client disconnected: {sid}")
        if sid in self.authenticated_sids:
            self.authenticated_sids.discard(sid)
            del self.user_info[sid]

    async def on_message(self, sid, data):
        if sid in self.authenticated_sids:
            room = data.get('room')
            message = data.get('message')

            if room in self.server.manager.rooms.keys():
                username = self.user_info[sid]
                self._rs.add_message(
                    chatroom_id=self.name,
                    username=username,
                    message=message
                )
                message = {
                    'username': username,
                    'message': message
                }
                await self.emit(event="message", data=message, room=room)

    async def on_join_room(self, sid, data):
        room = data.get('room')
        self.enter_room(sid, room)

    async def on_leave_room(self, sid, data):
        room = data.get('room')
        self.leave_room(sid, room)

    def create_room(self, room_name):
        self._rs.create_chatroom(room_name)

    def delete_room(self, room_name):
        # 몽고 저장도 여기서
        self.close_room(room_name)
        messages = self._rs.get_messages(room_name)
        self._rs.delete_chatroom(room_name)
        print(messages)
