from datetime import datetime as dt, time

from fastapi import status
from datetimerange import DateTimeRange

from ...db.db_sqlalchemy import SessionLocal
from ...utils.exceptions import JSONException
from ...models.schedule import ScheduleModel
from ...models.table import TableModel
from ...crud_operations.schedule import ScheduleOperation
from ...crud_operations.table import TableOperation


def find_daily_schedule(input_date: dt.date) -> ScheduleModel:
    """
    First it looks up a schedule by date in the database.
    If the schedule is not found searches it by day of the week.
    """
    specific_date_schedule: list[ScheduleModel] = _get_schedule_objects(day=input_date)
    if specific_date_schedule and len(specific_date_schedule) > 1:
        raise JSONException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            message=f"Found several same specific days '{input_date}'."
                                    f"Check your database.")

    elif specific_date_schedule:
        return specific_date_schedule[0]

    else:
        week_days: dict = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
        }
        input_weak_day_id: int = input_date.weekday()
        input_weak_day: str = week_days.get(input_weak_day_id)
        week_day_schedule: list[ScheduleModel] = _get_schedule_objects(day=input_weak_day)
        if not week_day_schedule:
            raise JSONException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                message=f"Given day of the week '{input_weak_day}' was not found."
                                        "You probably need to add 'schedules' first. "
                                        "Check your database.")
        elif len(week_day_schedule) > 1:
            raise JSONException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                message=f"Found several same days by name '{input_weak_day}'."
                                        "Check your database.")
        else:
            return week_day_schedule[0]


def convert_time_range_to_datetime_range(start_time: time,
                                         end_time: time,
                                         start_dt: dt,
                                         end_dt: dt):
    return DateTimeRange(start_dt.replace(hour=start_time.hour,
                                          minute=start_time.minute,
                                          second=start_time.second),
                         end_dt.replace(hour=end_time.hour,
                                        minute=end_time.minute,
                                        second=end_time.second)
                         )


def _db_session(func):
    def wrapper(*args, **kwargs):
        db = SessionLocal()
        try:
            return func(*args, **kwargs, db=db)
        finally:
            db.close()

    return wrapper


@_db_session
def _get_schedule_objects(schedule_ids: list = None, **kwargs) -> list[ScheduleModel]:
    if schedule_ids:
        result = [ScheduleOperation(db=kwargs.get('db')).find_by_id_or_404(table_id)
                  for table_id in schedule_ids]
    else:
        result = ScheduleOperation(db=kwargs.get('db')).find_all_by_params(**kwargs)
    return result


@_db_session
def _get_table_objects(table_ids: list = None, **kwargs) -> list[TableModel]:
    if table_ids:
        result = [TableOperation(db=kwargs.get('db')).find_by_id_or_404(table_id)
                  for table_id in table_ids]
    else:
        result = TableOperation(db=kwargs.get('db')).find_all_by_params(**kwargs)
    return result
