import socketio
from pydantic import BaseModel

from chat_app.auth import *
from fastapi import APIRouter, Depends

from chat_app.chat_namespace import ChatNamespace


def get_router(chat_namespace: ChatNamespace):

    router = APIRouter(
        prefix='/room'
    )

    @router.post("/{room_id}", dependencies=[Depends(JWTFilter(allow_role='ROLE_SYSTEM'))])
    async def create_room(room_name: str):
        chat_namespace.create_room(room_name)
        return "create_room " + room_name

    @router.delete("/{room_id}", dependencies=[Depends(JWTFilter(allow_role=['ROLE_ADMIN', 'ROLE_SYSTEM']))])
    async def delete_room(room_name: str):
        chat_namespace.delete_room(room_name)
        return "delete_room " + room_name

    @router.delete("/{room_id}/{chat_id}", dependencies=[Depends(JWTFilter(allow_role='ROLE_ADMIN'))])
    async def delete_chat(room_name: str, chat_id: str):
        # room_id 의 chat_id에 해당하는 요소의 값을 disable과 같이 비활성화 하기 + sio에서도 이벤트 발생시켜야 함
        return "delete_chat " + room_name + chat_id

    return router
