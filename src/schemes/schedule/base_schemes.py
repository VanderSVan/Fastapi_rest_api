from typing import Literal
from datetime import date, time
from datetime import datetime as dt
from datetime import timedelta as td

from pydantic import BaseModel, Field, root_validator

from src.schemes.validators.schedule import ScheduleValidator


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
    open_time: time = Field(..., example=dt.utcnow().strftime('%H:%M'))
    close_time: time = Field(..., example=(dt.utcnow() + td(hours=4)).strftime('%H:%M'))
    break_start_time: time | None = Field(None, example=dt.utcnow().strftime('%H:%M'))
    break_end_time: time | None = Field(None, example=(dt.utcnow() + td(hours=1)).strftime('%H:%M'))


class SchedulePatchSchema(ScheduleBaseSchema):

    @root_validator()
    def schedule_patch_validate(cls, values):
        validator = ScheduleValidator(values)
        return validator.validate_data()


class ScheduleDeleteSchema(ScheduleBaseSchema):
    pass


class SchedulePostSchema(ScheduleBaseSchema):

    @root_validator()
    def order_post_validate(cls, values):
        validator = ScheduleValidator(values)
        return validator.validate_data()


class ScheduleGetSchema(ScheduleBaseSchema):
    id: int

    class Config:
        orm_mode = True

