from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.meeting_room import meeting_room_crud
from app.crud.reservation import reservation_crud
# Так как в Python-пакете app.models модели импортированы в __init__.py,
# импортировать их можно прямо из пакета.
from app.models import MeetingRoom, Reservation, User


# Корутина, проверяющая уникальность полученного имени переговорки.
async def check_name_duplicate(
        room_name: str,
        session: AsyncSession,
) -> None:
    # Вызываем функцию проверки уникальности поля name:
    # Вторым параметром передаем сессию в CRUD-функцию:
    # room_id = await get_room_id_by_name(room_name, session)
    # Заменяем вызов функции на вызов мотода.
    room_id = await meeting_room_crud.get_room_id_by_name(room_name, session)
    # Если такой объект уже есть в базе - вызываем ошибку:
    if room_id is not None:
        raise HTTPException(
            status_code=422,
            detail='Переговорка с таким именем уже существует',
        )


# Оформляем повторяющийся код в виде отдельной корутины.
async def check_meeting_room_exists(
        meeting_room_id: int,
        session: AsyncSession,
) -> MeetingRoom:
    # meeting_room = await get_meeting_room_by_id(
    #     meeting_room_id, session
    # )
    # Заменяем вызов функции на вызов мотода.
    meeting_room = await meeting_room_crud.get(meeting_room_id, session)
    if meeting_room is None:
        raise HTTPException(
            # Для отсутствующего объекта вернем статус 404 - Not found.
            status_code=404,
            detail='Переговорка не найдена!'
        )
    return meeting_room


async def check_reservation_intersections(**kwargs) -> None:
    reservations = await reservation_crud.get_reservations_at_the_same_time(
        **kwargs
    )
    if reservations:
        raise HTTPException(
            status_code=422,
            detail=str(reservations)
        )


async def check_reservation_before_edit(
        reservation_id: int,
        session: AsyncSession,
        user: User,
) -> Reservation:
    reservation = await reservation_crud.get(
        # Для монятности кода можно передать аргументы по ключу.
        obj_id=reservation_id, session=session
    )
    if not reservation:
        raise HTTPException(status_code=404, detail='Бронь не найдена')
    if reservation.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='Невозможно редактировать или удалить чужую бронь!'
        )
    return reservation
