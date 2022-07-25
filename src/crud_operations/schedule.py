from datetime import date, datetime as dt

from sqlalchemy import and_

from .base_crud_operations import ModelOperation
from ..models.schedule import ScheduleModel
from ..schemas.schedule.base_schemas import SchedulePatchSchema


class ScheduleOperation(ModelOperation):
    def __init__(self, db):
        self.model = ScheduleModel
        self.patch_schema = SchedulePatchSchema
        self.response_elem_name = 'schedule'
        self.db = db

    def find_all_by_params(self, **kwargs) -> list[ScheduleModel]:
        _date = str(kwargs.get('day')) if isinstance(kwargs.get('day'), (dt, date)) else None
        _week_day = kwargs.get('day').capitalize() if isinstance(kwargs.get('day'), str) else None

        day = _date if _date else _week_day
        # print("ALOOOOOO", day, type(day))
        open_time = kwargs.get('open_time')
        close_time = kwargs.get('close_time')
        break_start_time = kwargs.get('break_start_time')
        break_end_time = kwargs.get('break_end_time')
        return (self.db
                    .query(ScheduleModel)
                    .filter(and_(
                                 (ScheduleModel.day == day
                                  if day is not None else True),
                                 (ScheduleModel.open_time <= open_time
                                  if open_time is not None else True),
                                 (ScheduleModel.close_time <= close_time
                                  if close_time is not None else True),
                                 (ScheduleModel.break_start_time <= break_start_time
                                  if break_start_time is not None else True),
                                 (ScheduleModel.break_end_time <= break_end_time
                                  if break_end_time is not None else True)
                                )
                            )
                    .all())
