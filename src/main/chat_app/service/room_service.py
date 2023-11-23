from chat_app.redis.redis_service import RedisService


class RoomService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self._rs = RedisService()
            cls._init = True

