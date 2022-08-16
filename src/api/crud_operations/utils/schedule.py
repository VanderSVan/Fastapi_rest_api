from datetime import time, datetime as dt
from typing import NoReturn

from sqlalchemy.orm import Session
from datetimerange import DateTimeRange
from fastapi import status

from src.api.models.schedule import ScheduleModel
from src.api.crud_operations.schedule import ScheduleOperation
from src.utils.exceptions import JSONException
from src.utils.response_generation.main import get_text
from src.utils.color_logging.main import logger


def check_time_range_within_schedule_range(start: dt, end: dt, db: Session) -> bool:
    """
    Returns True if the time is within the range of the daily schedule,
    else raises JSONException.
    :param start: input start datetime.
    :param end: input end datetime.
    :param db: database session.
    :return: True.
    :raises: JSONException, if the time range is not within the schedule range.
    """
    # get daily schedule by date or week day
    daily_schedule: ScheduleModel = find_schedule(start.date(), db)

    # convert time schedule range to datetime schedule range
    daily_schedule_without_break = _replace_time_range_to_datetime_range(
        daily_schedule.open_time,
        daily_schedule.close_time,
        start,
        end
    )
    # convert break time to break datetime
    break_schedule = _replace_time_range_to_datetime_range(
        daily_schedule.break_start_time,
        daily_schedule.break_end_time,
        start,
        end
    ) if start and end else None

    input_time_range = DateTimeRange(start, end)

    # check datetime ranges
    if break_schedule:
        _check_break_time_inside_input_time(break_schedule, input_time_range)

    if input_time_range not in daily_schedule_without_break:
        raise JSONException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=get_text('time_out_of_schedule').format(daily_schedule_without_break)
        )
    return True


def find_schedule(input_date: dt.date, db: Session) -> ScheduleModel:
    """
    First it looks up a schedule by date in the database.
    If the schedule is not found, searches it by day of the week.
    """
    specific_date_schedule: ScheduleModel = _find_specific_day_schedule(input_date, db)

    if specific_date_schedule:
        return specific_date_schedule
    else:
        return _find_week_day_schedule(input_date, db)


def _replace_time_range_to_datetime_range(start_time: time,
                                          end_time: time,
                                          start_dt: dt,
                                          end_dt: dt
                                          ) -> DateTimeRange | None:
    """
    Replaces time range to datetime range.
    Example: (10:00:00, 12:00:00) ->
    -> (2022-01-01T10:00:00, 2022-01-01T12:00:00)
    """
    if start_time and end_time:
        return DateTimeRange(
            start_dt.replace(hour=start_time.hour,
                             minute=start_time.minute,
                             second=start_time.second),
            end_dt.replace(hour=end_time.hour,
                           minute=end_time.minute,
                           second=end_time.second)
        )
    return None


def _check_break_time_inside_input_time(break_schedule: DateTimeRange,
                                        input_time_range: DateTimeRange
                                        ) -> NoReturn:
    """Checks break time range inside input time range"""
    if (
            break_schedule in input_time_range
            or str(input_time_range.start_datetime) in break_schedule
            or str(input_time_range.end_datetime) in break_schedule
    ):
        raise JSONException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=get_text('time_inside_break').format(break_schedule)
        )


def _find_specific_day_schedule(input_date: dt.date, db: Session) -> ScheduleModel | None:
    """
    Searches for specific days, such as holidays etc.
    For example: 2022-12-25 - Catholic Christmas.
    """
    specific_date_schedule: list[ScheduleModel] = _get_schedule_objects(db, day=input_date)
    if specific_date_schedule and len(specific_date_schedule) > 1:
        logger.exception(
            f"Found several same specific days '{input_date}'."
            f"Check your database."
        )
        raise JSONException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_text('err_500')
        )
    elif specific_date_schedule:
        return specific_date_schedule[0]
    else:
        return None


def _find_week_day_schedule(input_date: dt.date, db: Session) -> ScheduleModel:
    """Searches for schedule by day of the week."""
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
    week_day_schedule: list[ScheduleModel] = _get_schedule_objects(db, day=input_weak_day)
    if not week_day_schedule:
        logger.exception(
            f"Given day of the week '{input_weak_day}' was not found."
            f"You probably need to add 'schedules' first. "
            f"Check your database."
        )
        raise JSONException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_text('err_500')
        )
    elif len(week_day_schedule) > 1:
        logger.exception(
            f"Found several same days by name '{input_weak_day}'."
            f"Check your database."
        )
        raise JSONException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_text('err_500')
        )
    else:
        return week_day_schedule[0]


def _get_schedule_objects(db: Session,
                          schedule_ids: list = None,
                          **kwargs
                          ) -> list[ScheduleModel]:
    schedule_operation = ScheduleOperation(db=db, user=None)
    if schedule_ids:
        result = [schedule_operation.find_by_id_or_404(table_id)
                  for table_id in schedule_ids]
    else:
        result = schedule_operation.find_all_by_params(**kwargs)
    return result
