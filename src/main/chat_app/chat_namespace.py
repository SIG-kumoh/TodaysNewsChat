from typing import List, Dict
from dataclasses import dataclass
from socketio import AsyncNamespace
from fastapi.security import HTTPAuthorizationCredentials

from chat_app.redis.redis_service import RedisService
from chat_app.auth import TokenProvider, JWTFilter


@dataclass
class DummyRequest:
    headers: dict
    cookies: dict

    def __post_init__(self):
        self.cookies = {e.split('=')[0]: e.split('=')[1] for e in self.cookies.split('; ')}


class ChatNamespace(AsyncNamespace):
    def __init__(self, namespace):
        super().__init__(namespace=namespace)
        self.name = namespace
        self.authenticated_sids = set()
        self.user_info = dict()
        self._rs = RedisService()
        self._tp = TokenProvider()
        self._filter = JWTFilter()
        self.rooms: Dict[str, List[str]] = {}

    async def on_connect(self, sid, environ):
        try:
            request = DummyRequest(
                headers={'Authorization': environ.get('HTTP_AUTHORIZATION')},
                cookies=environ.get('HTTP_COOKIE')
            )
            http_credentials: HTTPAuthorizationCredentials = await self._filter(request)
            token = http_credentials.credentials
            user = self._tp.get_user(token)
            self.authenticated_sids.add(sid)
            self.user_info[sid] = user.username
        except:
            print(f"Invalid token. Allowing connection: {sid}")

    async def on_disconnect(self, sid):
        for room_name in self.rooms.keys():
            self.leave_room(sid, room_name)
        print(f"Client disconnected: {sid}")
        if sid in self.authenticated_sids:
            self.authenticated_sids.discard(sid)
            del self.user_info[sid]

    async def on_message(self, sid, data):
        if sid in self.authenticated_sids:
            room_name = data.get('room')
            message = data.get('message')
            if room_name in self.rooms.keys() and sid in self.rooms[room_name]:
                username = self.user_info[sid]
                self._rs.add_message(
                    room_name=room_name,
                    username=username,
                    message=message
                )
                message = {
                    'username': username,
                    'message': message
                }
                await self.emit(event="message", data=message, room=room_name)

    async def on_join_room(self, sid, data):
        room_name = data.get('room')
        if room_name in self.rooms.keys():
            self.rooms[room_name].append(sid)
            self.enter_room(sid, room_name)
            await self.emit(event='join_room', data=f'sid : {sid} join room {room_name}', to=sid)
        else:
            await self.emit(event='join_room', data=f'CAN NOT FOUND : {room_name} ', to=sid)

    async def on_leave_room(self, sid, data):
        room = data.get('room')
        if room in self.rooms.keys():
            await self.emit(event='leave_room', data=f'sid : {sid} leave room {room}', to=sid)
            self.rooms[room].remove(sid)
            self.leave_room(sid, room)
        else:
            await self.emit(event='leave_room', data=f'CAN NOT FOUND : {room} ', to=sid)

    async def create_room(self, room_name: str):
        if room_name not in self.rooms.keys():
            self.rooms[room_name] = []
            self._rs.create_chatroom(room_name)

    async def delete_room(self, room_name: str):
        # 몽고 저장도 여기서
        if room_name in self.rooms.keys():
            await self.emit(event='leave_room', data=f'ROOM CLOSED {room_name}', room=room_name)
            del self.rooms[room_name]
            await self.close_room(room_name)

            messages = self._rs.get_messages(room_name)
            self._rs.delete_chatroom(room_name)
            print(messages)
