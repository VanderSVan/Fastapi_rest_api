from sqlalchemy import and_

from .base_crud_operations import ModelOperation
from ..models.schedule import ScheduleModel


class ScheduleOperation(ModelOperation):

    def find_all_by_params(self, **kwargs) -> list[ScheduleModel]:
        day = kwargs.get('day').capitalize() if kwargs.get('day') else None
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
                    .all())
