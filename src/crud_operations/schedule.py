from datetime import date, datetime as dt

from fastapi import status
from sqlalchemy import and_

from src.models.schedule import ScheduleModel
from src.schemes.schedule.base_schemes import SchedulePatchSchema
from src.crud_operations.base_crud_operations import ModelOperation
from src.schemes.validators.schedule import SchedulePostOrPatchValidator
from src.utils.exceptions import JSONException
from src.utils.responses.main import get_text


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

    def update_obj(self, id_: int, new_data: SchedulePatchSchema) -> ScheduleModel:
        """
        Updates schedule values into db with new data.
        If the user does not have access rights, then the error is raised.
        :param id_: schedule id.
        :param new_data: new schedule data to update.
        :return: updated schedule.
        """
        # Get schedule object from db or raise 404 exception.
        # This is where user access is checked.
        old_schedule: ScheduleModel = self.find_by_id_or_404(id_)

        # Prepare new data.
        prepared_new_data: SchedulePatchSchema = self._prepare_data_for_patch_operation(old_schedule, new_data)

        # Update schedule.
        for key, value in prepared_new_data:
            if hasattr(old_schedule, key):
                setattr(old_schedule, key, value)

        # Save updated schedule.
        updated_schedule: ScheduleModel = old_schedule
        self.db.commit()
        self.db.refresh(updated_schedule)

        return updated_schedule
    
    def _prepare_data_for_patch_operation(self,
                                          old_schedule: ScheduleModel,
                                          new_data: SchedulePatchSchema
                                          ) -> SchedulePatchSchema:
        """
        Executes all necessary checks to update the schedule data.
        :param old_schedule: data from db.
        :param new_data: schedule update data.
        :return: updated data.
        """
        # Extract schedule data by scheme.
        old_schedule_data: SchedulePatchSchema = self.patch_schema(**old_schedule.__dict__)

        # Update schedule data.
        data_to_update: dict = new_data.dict(exclude_unset=True)  # remove fields where value is None
        if data_to_update:
            updated_data: SchedulePatchSchema = old_schedule_data.copy(update=data_to_update)  # replace only changed data
        else:
            raise JSONException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=get_text('err_patch_no_data')
            )

        # Check time values, required if only one time field was given.
        SchedulePostOrPatchValidator.check_open_close_time(
            updated_data.open_time, updated_data.close_time
        )
        SchedulePostOrPatchValidator.check_break_time(
            updated_data.break_start_time, updated_data.break_end_time
        )
        return updated_data
