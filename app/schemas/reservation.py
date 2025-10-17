from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Extra, Field, root_validator, validator


# Представить объект datetime в виде строки с точностью до минут.
FROM_TIME = (
    datetime.now() + timedelta(minutes=10)
).isoformat(timespec='minutes')
TO_TIME = (
    datetime.now() + timedelta(hours=1)
).isoformat(timespec='minutes')


class ReservationBase(BaseModel):
    from_reserve: datetime = Field(..., example=FROM_TIME)
    to_reserve: datetime = Field(..., example=TO_TIME)

    class Config:
        extra = Extra.forbid


# Схема для получения данных.
class ReservationUpdate(ReservationBase):
    @validator('from_reserve')
    def check_from_reserve_later_than_now(cls, value):
        if value <= datetime.now():
            raise ValueError(
                'Время начала бронирования '
                'не может быть меньше текущего времени'
            )
        return value
    
    @root_validator(skip_on_failure=True)
    def check_from_reserve_before_to_reserve(cls, values):
        if values['from_reserve'] >= values['to_reserve']:
            raise ValueError(
                'Время начала бронирования '
                'не может быть больше времени окончания'
            )
        return values


# Схема для получения данных.
# Этот класс наследуем от ReservationUpdate с валидаторами.
class ReservationCreate(ReservationUpdate):
    meetingroom_id: int


# Схема для возвращаемого объекта.
# Класс ReservationDB нельзя наследовать от ReservationCreate:
# тогда унаследуется и валидатор check_from_reserve_later_than_now,
# и при получении старых объектов из БД он будет выдавать ошибку валидации:
# ведь их from_reserve вполне может быть меньше текущего времени.
class ReservationDB(ReservationBase):
    id: int
    meetingroom_id: int
    # Добавляем опциональное поле user_id.
    user_id: Optional[int]

    class Config:
        orm_mode = True
