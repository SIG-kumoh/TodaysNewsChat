import socketio

from fastapi import APIRouter


def get_router(sio: socketio.AsyncServer):
    # TODO make service instance

    router = APIRouter(
        prefix='/room'
    )

    # TODO 시스템 이상의 권한
    @router.post("")
    async def create_room():
        # sio 에 특정 규칙에 의해 생성된 Namespace, redis 채팅방 만들기
        return "create_room"

    # TODO 관리자 이상의 권한
    @router.delete("/{room_id}")
    async def delete_room(room_id: str):
        # room_id 에 해당하는 Namespace를 Mongo 에 저장하고, Namespace, redis 채팅방 삭제
        return "delete_room " + room_id

    # TODO 관리자 이상의 권한
    @router.delete("/{room_id}/{chat_id}")
    async def delete_chat(room_id: str, chat_id: str):
        # room_id 의 chat_id에 해당하는 요소의 값을 disable과 같이 비활성화 하기 + sio에서도 이벤트 발생시켜야 함
        return "delete_chat " + room_id + chat_id

    return router
