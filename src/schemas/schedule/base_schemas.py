from typing import Literal
from datetime import date, time

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
    open_time: time = "08:00"
    close_time: time = "17:00"
    break_start_time: time = None
    break_end_time: time = None


class SchedulePutSchema(ScheduleBaseSchema):
    pass


class ScheduleDeleteSchema(ScheduleBaseSchema):
    pass


class SchedulePostSchema(ScheduleBaseSchema):
    pass


class ScheduleGetSchema(ScheduleBaseSchema):
    id: int

    class Config:
        orm_mode = True

