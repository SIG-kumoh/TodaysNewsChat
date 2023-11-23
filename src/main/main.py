from chat_app import ChatApp
from chat_app.redis.redis_service import RedisService

if __name__ == '__main__':
    try:
        server = ChatApp()
        server.run()

    except Exception as e:
        print(e)
