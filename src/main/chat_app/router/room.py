import socketio
from pydantic import BaseModel

from chat_app.auth import *
from fastapi import APIRouter, Depends

from chat_app.chat_namespace import ChatNamespace


def get_router(chat_namespace: ChatNamespace):
    router = APIRouter(
        prefix='/room'
    )

    @router.delete("", dependencies=[Depends(JWTFilter(allow_role='ROLE_SYSTEM'))])
    async def delete_all_room():
        await chat_namespace.delete_all_room()

    @router.post("/{room_name}", dependencies=[Depends(JWTFilter(allow_role='ROLE_SYSTEM'))])
    async def create_room(room_name: str):
        await chat_namespace.create_room(room_name)

    @router.delete("/{room_name}", dependencies=[Depends(JWTFilter(allow_role=['ROLE_ADMIN', 'ROLE_SYSTEM']))])
    async def delete_room(room_name: str):
        await chat_namespace.delete_room(room_name)

    @router.delete("/{room_name}/{chat_id}", dependencies=[Depends(JWTFilter(allow_role=['ROLE_ADMIN', 'ROLE_SYSTEM']))])
    async def delete_chat(room_name: str, chat_id: int):
        await chat_namespace.message_disable(room_name, chat_id)

    return router

