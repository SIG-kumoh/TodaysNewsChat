from fastapi import APIRouter

router = APIRouter(
    prefix="/room"
)


#TODO 시스템 이상의 권한
@router.post("")
async def create_room():
    pass


# TODO 관리자 이상의 권한
@router.delete("/{room_id}")
async def delete_room(room_id: str):
    pass


# TODO 관리자 이상의 권한
@router.delete("/{room_id}/{chat_id}")
async def get_stat_per_hour(room_id: str, chat_id: str):
    pass
