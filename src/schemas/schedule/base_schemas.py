from typing import Literal
from datetime import date, time
from datetime import datetime as dt

from pydantic import BaseModel, Field


class ScheduleBaseSchema(BaseModel):
    day: (Literal['Monday'] |
          Literal['Tuesday'] |
          Literal['Wednesday'] |
          Literal['Thursday'] |
          Literal['Friday'] |
          Literal['Saturday'] |
          Literal['Sunday'] |
          date
          )
    open_time: time = Field(dt.utcnow().strftime('%H:%M'))
    close_time: time = Field(dt.utcnow().strftime('%H:%M'))
    break_start_time: time | None = Field(dt.utcnow().strftime('%H:%M'))
    break_end_time: time | None = Field(dt.utcnow().strftime('%H:%M'))


class SchedulePatchSchema(ScheduleBaseSchema):
    pass


class ScheduleDeleteSchema(ScheduleBaseSchema):
    pass


class SchedulePostSchema(ScheduleBaseSchema):
    pass


class ScheduleGetSchema(ScheduleBaseSchema):
    id: int

    class Config:
        orm_mode = True

