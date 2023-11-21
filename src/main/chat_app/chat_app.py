import asyncio
import socketio

from fastapi import FastAPI, APIRouter

from ._app import APP
from .chat_namespace import ChatNamespace
from .router import *


class ChatApp(APP):
    def __init__(self):
        super().__init__()
        self._app = FastAPI()
        self._sio = socketio.AsyncServer(async_mode='asgi',
                                         cors_allowed_origins='*',)
        self._loop = asyncio.get_event_loop()

        self._configure_event()
        self._configure_routes()
        self._test_configure()

        self._socket_app = socketio.ASGIApp(self._sio, self._app)

    def _configure_event(self):
        pass

    def _configure_routes(self):
        root_router = APIRouter(prefix='/chat')

        room_router = get_room_router(self._sio)

        root_router.include_router(room_router)

        self._app.include_router(root_router)

    def run(self):
        try:
            self._loop = asyncio.get_event_loop()
            server = self._server_load(self._socket_app)

            self._loop.run_until_complete(server.serve())
        except Exception as e:
            print(f"An error occurred: {e}")

    def _test_configure(self):
        self._sio.register_namespace(ChatNamespace('/chat/conn/1'))
