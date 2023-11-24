import json
import redis

from datetime import datetime


class RedisService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self._rd = redis.StrictRedis(host='192.168.0.2', port=6379, password='admin')
            cls._init = True

    def delete_refresh_token_by_redis(self, username: str) -> None:
        self._rd.delete(username)

    def get_refresh_token_by_redis(self, username: str) -> str:
        return self._rd.get(username)

    def exists_access_token_in_redis(self, access_token):
        return self._rd.exists(access_token)

    def create_chatroom(self, room_name):
        self._rd.sadd('chat_rooms', room_name)

    def delete_chatroom(self, room_name):
        self._rd.srem('chat_rooms', room_name)
        self._rd.delete(f'chat_room:{room_name}')

    def get_messages(self, room_name, start_idx=0, end_idx=-1):
        messages = self._rd.lrange(f'chat_room:{room_name}', start_idx, end_idx)
        return list(map(lambda e: json.loads(e), messages))

    def add_message(self, room_name, username, message):
        message_data = {
            'username': username,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        message_data = json.dumps(message_data, ensure_ascii=False)
        redis_key = f'chat_room:{room_name}'
        self._rd.rpush(redis_key, message_data)
