import asyncio
import socketio

from fastapi import FastAPI

from ._app import APP
from .router import *


class ChatApp(APP):
    def __init__(self):
        self.app = FastAPI()
        self.sio = socketio.AsyncServer(async_mode='asgi',
                                        cors_allowed_origins='*',)
        self.loop = asyncio.get_event_loop()

        self._configure_event()
        self._configure_routes()

        self.socket_app = socketio.ASGIApp(self.sio, self.app)

    def _configure_event(self):
        pass

    def _configure_routes(self):
        self.app.include_router(room_router)

    def run(self):
        try:
            self.loop = asyncio.get_event_loop()
            server = self._server_load(self.socket_app)

            self.loop.run_until_complete(server.serve())
        except Exception as e:
            print(f"An error occurred: {e}")
