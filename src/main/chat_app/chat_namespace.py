from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, asdict
from socketio import AsyncNamespace
from fastapi.security import HTTPAuthorizationCredentials

from chat_app.chat_database import ChatDatabase
from chat_app.auth import TokenProvider, JWTFilter


@dataclass
class Message:
    id          : int
    username    : str
    message     : str
    regdate     : datetime
    activated   : bool


@dataclass
class DummyRequest:
    headers: dict
    cookies: dict

    def __post_init__(self):
        self.cookies = {e.split('=')[0]: e.split('=')[1] for e in self.cookies.split('; ')}


class Room:
    name            : str
    verified_list   : List[str]
    database        : ChatDatabase

    def __init__(self, name, db_directory):
        self.name = name
        self.verified_list = []
        self.database = ChatDatabase(
            directory=db_directory,
            name=name
        )

    def join(self, sid: str):
        if sid not in self.verified_list:
            self.verified_list.append(sid)

    def leave(self, sid: str):
        if sid in self.verified_list:
            self.verified_list.remove(sid)

    def save_message(self, username, message):
        return Message(*self.database.save_message(username, message))

    def message_disable(self, message_id):
        self.database.message_disable(message_id)

    def get_all_message(self):
        return [Message(*e) for e in self.database.find_all_message()]

    def is_verified(self, sid):
        return sid in self.verified_list


class ChatNamespace(AsyncNamespace):
    def __init__(self, namespace, db_directory):
        super().__init__(namespace=namespace)
        self.db_directory = db_directory

        self.authenticated_sids = set()
        self.user_info = dict()
        self._tp = TokenProvider()
        self._filter = JWTFilter()
        self.rooms: Dict[str, Room] = {}

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
            print(f"Invalid token. Non-Verified connection: {sid}")

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
            if room_name in self.rooms.keys() and self.rooms[room_name].is_verified(sid):
                username = self.user_info[sid]
                message = self.rooms[room_name].save_message(username, message)
                await self.emit(event="message", data=asdict(message), room=room_name)

    async def on_join_room(self, sid, data):
        room_name = data.get('room')
        if room_name in self.rooms.keys():
            self.rooms[room_name].join(sid)
            self.enter_room(sid, room_name)
            messages = self.rooms[room_name].get_all_message()

            await self.emit(event='join_room', data=f'sid : {sid} join room {room_name}', to=sid)
            await self.emit(event='initialize', data=[asdict(m) for m in messages], to=sid)
        else:
            await self.emit(event='join_room', data=f'CAN NOT FOUND : {room_name} ', to=sid)

    async def on_leave_room(self, sid, data):
        room = data.get('room')
        if room in self.rooms.keys():
            await self.emit(event='leave_room', data=f'sid : {sid} leave room {room}', to=sid)
            self.rooms[room].leave(sid)
            self.leave_room(sid, room)
        else:
            await self.emit(event='leave_room', data=f'CAN NOT FOUND : {room} ', to=sid)

    async def create_room(self, room_name: str):
        if room_name not in self.rooms.keys():
            self.rooms[room_name] = Room(name=room_name, db_directory=self.db_directory)

    async def delete_room(self, room_name: str):
        if room_name in self.rooms.keys():
            await self.emit(event='leave_room', data=f'ROOM CLOSED {room_name}', room=room_name)
            del self.rooms[room_name]
            await self.close_room(room_name)

    async def message_disable(self, room_name: str, message_id: int):
        if room_name in self.rooms.keys():
            self.rooms[room_name].message_disable(message_id)
            message = {'message_id': message_id}
            await self.emit(event="message_disable", data=message, room=room_name)

    async def delete_all_room(self):
        room_names = list(self.rooms.keys())
        for room_name in room_names:
            await self.emit(event='leave_room', data=f'ROOM CLOSED {room_name}', room=room_name)
            del self.rooms[room_name]
            await self.close_room(room_name)
