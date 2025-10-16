from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_meeting_room_exists, check_reservation_intersections
)
from app.core.db import get_asinc_session
from app.crud.reservation import reservation_crud
from app.schemas.reservation import ReservationCreate, ReservationDB
from app.schemas.meeting_room import MeetingRoomDB


router = APIRouter()


@router.post('/', response_model=ReservationDB)
async def create_reservation(
        reservation: ReservationCreate,
        session: AsyncSession = Depends(get_asinc_session)
):
    await check_meeting_room_exists(
        reservation.meetingroom_id, session
    )
    await check_reservation_intersections(
        # Так как валидатор принимает **kwargs,
        # аргументы должны быть переданы с указанием ключей.
        **reservation.dict(), session=session
    )
    new_reservation = await reservation_crud.create(
        reservation, session
    )
    return new_reservation


@router.get(
    '/',
    response_model=list[ReservationDB]
)
async def get_all_reservations(
    session: AsyncSession = Depends(get_asinc_session)
):
    reservations = await reservation_crud.get_multi(session)
    return reservations
    

