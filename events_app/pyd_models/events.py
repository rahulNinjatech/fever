from datetime import date
from datetime import datetime
from datetime import time
from typing import List

from events_app.database_manager.schemas import EventSchema
from pydantic import UUID4
from pydantic import BaseModel
from pydantic import model_validator


class EventModel(BaseModel):
    id: UUID4
    title: str
    event_id: int
    start_date: date
    start_time: time
    end_date: date
    end_time: time
    min_price: float
    max_price: float

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    def convert_datetime_to_date_and_time(cls, _input):
        if isinstance(_input, EventSchema):
            result = {
                "id": _input.id,
                "title": _input.title,
                "event_id": _input.event_id,
                "min_price": _input.min_price,
                "max_price": _input.max_price,
                "start_date": _input.start_date_time.date(),
                "start_time": _input.start_date_time.time(),
                "end_date": _input.end_date_time.date(),
                "end_time": _input.end_date_time.time(),
            }
            return result
        return _input


class PostEventModel(BaseModel):
    event_id: int
    base_event_id: int
    title: str
    start_date_time: datetime
    end_date_time: datetime
    min_price: float
    max_price: float

    class Config:
        from_attributes = True


class ResponseEventModel(BaseModel):
    events: List[EventModel]


class ErrorModel(BaseModel):
    code: str
    message: str


class StandardResponseModel(BaseModel):
    data: ResponseEventModel = None
    error: ErrorModel = None
