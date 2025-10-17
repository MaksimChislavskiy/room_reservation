from fastapi import APIRouter, Depends

# Импортируем класс асинхронной сессии для аннотации параметра.
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
# from app.crud.meeting_room import (
#     create_meeting_room, delete_meeting_room,
#     get_meeting_room_by_id, get_room_id_by_name,
#     read_all_rooms_from_db, update_meeting_room
# )
# Добавляем импорт зависимости, определяющей,
# что текущий пользователь - суперюзер.
from app.core.user import current_superuser
# Вместо импортов 6 функций импортируем объект meeting_room_crud.
from app.crud.meeting_room import meeting_room_crud
from app.crud.reservation import reservation_crud
# Импортируем схему ответа MeetingRoomDB.
from app.schemas.meeting_room import (
    MeetingRoomCreate, MeetingRoomDB, MeetingRoomUpdate
)
from app.schemas.reservation import ReservationDB
from app.api.validators import check_meeting_room_exists, check_name_duplicate

# router = APIRouter(
#     prefix='/meeting_rooms',
#     tags=['Meeting Rooms']
# )
router = APIRouter()


@router.post(
    '/',
    # Указываем схему ответа.
    response_model=MeetingRoomDB,
    response_model_exclude_none=True,
    # Добавляем вызов зависимости при обработке запроса.
    dependencies=[Depends(current_superuser)]
)
async def create_new_meeting_room(
    meeting_room: MeetingRoomCreate,
    # Указываем зависимость, предоставляющую объект сессии,
    # как параметр функции.
    session: AsyncSession = Depends(get_async_session),
):
    # Добавляем докстринг для большей информативности.
    """Только для суперюзеров."""
    # Выносим проверку дубликата имени в отдельную корутину.
    # Если такое имя уже существует, то будет вызвана ошибка HTTPException
    # и обработка запроса остановится.
    await check_name_duplicate(meeting_room.name, session)
    # Вторым параметром передаем сессию в CRUD-функцию:
    # new_room = await create_meeting_room(meeting_room, session)
    # Заменяем вызов функции на вызов мотода.
    new_room = await meeting_room_crud.create(meeting_room, session)
    return new_room


@router.get(
    '/',
    response_model=list[MeetingRoomDB],
    response_model_exclude_none=True,
)
async def get_all_meeting_rooms(
    session: AsyncSession = Depends(get_async_session)
):
    # all_rooms = await read_all_rooms_from_db(session)
    # Заменяем вызов функции на вызов мотода.
    all_rooms = await meeting_room_crud.get_multi(session)
    return all_rooms


@router.patch(
    # ID обновляемого объекта будет передаваться path-параметром.
    '/{meeting_room_id}',
    response_model=MeetingRoomDB,
    response_model_exclude_none=True,
    # Добавляем вызов зависимости при обработке запроса.
    dependencies=[Depends(current_superuser)]
)
async def partially_update_meeting_room(
    # ID обновляемого объекта.
    meeting_room_id: int,
    # JSON-данные, отправленные пользователем.
    obj_in: MeetingRoomUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    # Добавляем докстринг для большей информативности.
    """Только для суперюзеров."""
    # Получаем объект из БД по ID.
    # В ответ ожидается либо None, либо объект класс MeetingRoom.
    meeting_room = await check_meeting_room_exists(
        meeting_room_id, session
    )

    if obj_in.name is not None:
        # Если в запросе получено поле name - проверяем его на уникальность.
        await check_name_duplicate(obj_in.name, session)

    # Передаем в корутину все необходимые для обновления данные.
    # meeting_room = await update_meeting_room(
    #     meeting_room, obj_in, session
    # )
    # Заменяем вызов функции на вызов мотода.
    meeting_room = await meeting_room_crud.update(
        meeting_room, obj_in, session
    )
    return meeting_room


@router.delete(
    '/{meeting_room_id}',
    response_model=MeetingRoomDB,
    response_model_exclude_none=True,
    # Добавляем вызов зависимости при обработке запроса.
    dependencies=[Depends(current_superuser)]
)
async def remove_meeting_room(
    meeting_rom_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    # Добавляем докстринг для большей информативности.
    """Только для суперюзеров."""
    meeting_rom = await check_meeting_room_exists(
        meeting_rom_id, session
    )
    # meeting_rom = await delete_meeting_room(
    #     meeting_rom, session
    # )
    # Заменяем вызов функции на вызов мотода.
    meeting_room = await meeting_room_crud.remove(meeting_rom, session)
    return meeting_room


@router.get(
    '/{meeting_room_id}/reservations',
    response_model=list[ReservationDB],
    # Добавляем множество с полями, которые надо исключить из ответа.
    response_model_exclude={'user_id'},
)
async def get_reservations_for_room(
    meeting_room_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    await check_meeting_room_exists(meeting_room_id, session)
    reservations = await reservation_crud.get_future_reservations_for_room(
        room_id=meeting_room_id, session=session
    )
    return reservations