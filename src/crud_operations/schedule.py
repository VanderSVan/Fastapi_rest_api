from datetime import date, datetime as dt

from sqlalchemy import and_

from src.models.schedule import ScheduleModel
from src.schemes.schedule.base_schemes import SchedulePatchSchema
from src.crud_operations.base_crud_operations import ModelOperation


class ScheduleOperation(ModelOperation):
    def __init__(self, db, user):
        self.model = ScheduleModel
        self.model_name = 'schedule'
        self.patch_schema = SchedulePatchSchema
        self.db = db
        self.user = user

    def find_all_by_params(self, **kwargs) -> list[ScheduleModel]:
        """
        Finds all schedules in the db by given parameters.
        :param kwargs: dictionary with parameters.
        :return: schedules list or an empty list if no schedules were found.
        """
        _date = str(kwargs.get('day')) if isinstance(kwargs.get('day'), (dt, date)) else None
        _week_day = kwargs.get('day').capitalize() if isinstance(kwargs.get('day'), str) else None

        day = _date if _date else _week_day
        open_time = kwargs.get('open_time')
        close_time = kwargs.get('close_time')
        break_start_time = kwargs.get('break_start_time')
        break_end_time = kwargs.get('break_end_time')

        return (self.db
                    .query(ScheduleModel)
                    .filter(and_(
                                 (ScheduleModel.day == day
                                  if day is not None else True),
                                 (ScheduleModel.open_time >= open_time
                                  if open_time is not None else True),
                                 (ScheduleModel.close_time <= close_time
                                  if close_time is not None else True),
                                 (ScheduleModel.break_start_time >= break_start_time
                                  if break_start_time is not None else True),
                                 (ScheduleModel.break_end_time <= break_end_time
                                  if break_end_time is not None else True)
                                )
                            )
                    .all()
                )
