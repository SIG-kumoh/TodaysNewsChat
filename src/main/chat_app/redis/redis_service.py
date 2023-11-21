import redis


class RedisService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self._rd = redis.StrictRedis(host='202.31.202.34', port=6379)
            cls._init = True

    def delete_refresh_token_by_redis(self, username: str) -> None:
        self._rd.delete(username)

    def get_refresh_token_by_redis(self, username: str) -> str:
        return self._rd.get(username)
