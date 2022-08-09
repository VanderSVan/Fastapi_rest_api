from typing import NoReturn
from datetime import time, datetime as dt
from datetime import timedelta as td
from math import ceil

from sqlalchemy.orm import Session
from fastapi import status
from datetimerange import DateTimeRange

from src.api.models.order import OrderModel
from src.api.models.schedule import ScheduleModel
from src.api.models.table import TableModel
from src.api.crud_operations.schedule import ScheduleOperation
from src.api.crud_operations.table import TableOperation
from src.utils.color_logging.main import logger
from src.utils.exceptions import JSONException
from src.utils.response_generation.main import get_text


class OrderUtils:
    """
    !WARNING!
    This class cannot be used in ScheduleOperation and TableOperation classes,
    otherwise there will be an error with circular imports.
    """

    @classmethod
    def check_time_range_within_schedule_range(cls,
                                               start: dt,
                                               end: dt,
                                               schedule_operation: ScheduleOperation
                                               ) -> bool:
        """
        Returns True if the time is within the range of the daily schedule,
        else raises JSONException.
        :param start: input start time range.
        :param end: input end time range.
        :param schedule_operation: class for operations with obj schedule.
        :return: True.
        ":raises: JSONException, if the time range is not within the schedule range.
        """
        # get daily schedule by date or week day
        daily_schedule: ScheduleModel = cls._find_schedule(start.date(), schedule_operation)

        # convert time schedule range to datetime schedule range
        daily_schedule_without_break = replace_time_range_within_datetime_range(
            daily_schedule.open_time,
            daily_schedule.close_time,
            start,
            end
        )

        # convert break time to break datetime
        break_schedule = replace_time_range_within_datetime_range(
            daily_schedule.break_start_time,
            daily_schedule.break_end_time,
            start,
            end
        )
        input_time_range = DateTimeRange(start, end)

        # check datetime ranges
        if (
                break_schedule in input_time_range
                or str(input_time_range.start_datetime) in break_schedule
                or str(input_time_range.end_datetime) in break_schedule
        ):
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="The time range cannot be during the break time. "
                                        f"In this case break time = ({break_schedule})")

        elif input_time_range not in daily_schedule_without_break:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="The time range must be during the daily schedule. "
                                        f"In this case daily schedule = ({daily_schedule_without_break})")
        else:
            return True

    @staticmethod
    def check_free_time_in_orders(orders_for_day: list[OrderModel], start: dt, end: dt) -> bool:
        """Returns True if time is free else False"""
        input_time_range = DateTimeRange(start, end)
        occupied_orders: list[OrderModel] = [
            order
            for order in orders_for_day
            if (
                    DateTimeRange(order.start_datetime, order.end_datetime) in input_time_range
                    or
                    str(start) in DateTimeRange(order.start_datetime, order.end_datetime)
                    or
                    str(end) in DateTimeRange(order.start_datetime, order.end_datetime)
            )
        ]
        return False if occupied_orders else True

    @staticmethod
    def calculate_cost(start: dt, end: dt, tables: list[TableModel]) -> float:
        """
        Calculates order cost by table.price_per_hour
        Any timedelta is rounded to the hour.
        """
        hours: int = round_timedelta_to_hours(start, end)
        table_prices_per_hour: list = [table.price_per_hour for table in tables]
        total_price: float = sum(table_prices_per_hour)
        return hours * total_price

    @classmethod
    def add_or_delete_order_tables(cls,
                                   action: str,
                                   new_table_ids: list[int],
                                   existing_tables: list[TableModel],
                                   db: Session
                                   ) -> NoReturn:
        """
        Adds or deletes tables from order.
        If the tables that is given for method 'add_tables' does not exist then raises exception.
        If the tables that is given for method 'delete_tables' does not exist then nothing happens.
        :param action: table action - delete or add.
        :param new_table_ids: new table numbers.
        :param existing_tables: existing table objects.
        :param db: db session.
        """
        if action == 'tables':
            raise JSONException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=get_text('err_patch').format('add_tables', 'delete_tables', 'tables')
            )
        if action == 'add_tables' and new_table_ids:
            # If the table exists, add it or raise exception.
            table_operation = TableOperation(db=db, user=None)
            new_tables: list[TableModel] = cls._collect_new_tables_by_id(new_table_ids,
                                                                         existing_tables,
                                                                         table_operation)
            existing_tables.extend(new_tables)

        elif action == 'delete_tables' and new_table_ids:
            # If the table exists, delete it or do nothing.
            for table_number, table in enumerate(existing_tables):
                if table.id in new_table_ids:
                    del existing_tables[table_number]

    @staticmethod
    def convert_ids_to_table_objs(table_ids: list[int],
                                  table_operation: TableOperation
                                  ) -> list[TableModel]:
        """Converts integers to TableModel objects for nested model."""
        return [table_operation.find_by_id_or_404(table_id) for table_id in table_ids]

    @staticmethod
    def _collect_new_tables_by_id(new_table_ids: list[int],
                                  existing_tables: list[TableModel],
                                  table_operation: TableOperation
                                  ) -> list[TableModel]:
        """Creates a list with new tables excluding existing ones."""
        existing_table_ids: list[int] = [table_obj.id for table_obj in existing_tables]
        return [table_operation.find_by_id_or_404(table_id)
                for table_id in new_table_ids
                if table_id not in existing_table_ids]

    @classmethod
    def _find_schedule(cls,
                       input_date: dt.date,
                       schedule_operation: ScheduleOperation
                       ) -> ScheduleModel:
        """
        First it looks up a schedule by date in the database.
        If the schedule is not found searches it by day of the week.
        """
        specific_date_schedule: ScheduleModel = cls._find_specific_day_schedule(input_date,
                                                                                schedule_operation)
        if specific_date_schedule:
            result = specific_date_schedule

        else:
            result = cls._find_week_day_schedule(input_date, schedule_operation)

        return result

    @classmethod
    def _find_specific_day_schedule(cls,
                                    input_date: dt.date,
                                    schedule_operation: ScheduleOperation
                                    ) -> ScheduleModel | None:
        specific_date_schedule: list[ScheduleModel] = cls._get_schedule_objects(schedule_operation,
                                                                                day=input_date)
        if specific_date_schedule and len(specific_date_schedule) > 1:
            logger.exception(f"Found several same specific days '{input_date}'."
                             f"Check your database.")
            raise JSONException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                message=get_text('err_500')
                                )

        elif specific_date_schedule:
            return specific_date_schedule[0]

        else:
            return None

    @classmethod
    def _find_week_day_schedule(cls,
                                input_date: dt.date,
                                schedule_operation: ScheduleOperation
                                ) -> ScheduleModel:
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
        week_day_schedule: list[ScheduleModel] = cls._get_schedule_objects(schedule_operation,
                                                                           day=input_weak_day)
        if not week_day_schedule:
            logger.exception(f"Given day of the week '{input_weak_day}' was not found."
                             f"You probably need to add 'schedules' first. "
                             f"Check your database.")
            raise JSONException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                message=get_text('err_500')
                                )
        elif len(week_day_schedule) > 1:
            logger.exception(f"Found several same days by name '{input_weak_day}'."
                             f"Check your database.")
            raise JSONException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                message=get_text('err_500')
                                )
        else:
            return week_day_schedule[0]

    @staticmethod
    def _get_schedule_objects(schedule_operation: ScheduleOperation,
                              schedule_ids: list = None,
                              **kwargs
                              ) -> list[ScheduleModel]:
        if schedule_ids:
            result = [schedule_operation.find_by_id_or_404(table_id)
                      for table_id in schedule_ids]
        else:
            result = schedule_operation.find_all_by_params(**kwargs)
        return result


def round_timedelta_to_hours(start: dt, end: dt) -> int:
    """
    Rounds time delta to hours.
    Cuts off seconds and milliseconds.
    """
    dt_delta: td = end - start
    accurate_time_in_seconds: float = dt_delta.seconds / 3600
    return ceil(accurate_time_in_seconds)


def replace_time_range_within_datetime_range(start_time: time,
                                             end_time: time,
                                             start_dt: dt,
                                             end_dt: dt):
    """
    Replaces time range within datetime range.
    :param start_time: input start time.
    :param end_time: input end time.
    :param start_dt: input start datetime.
    :param end_dt: input end datetime.
    :return: changed datetime range.
    """
    return DateTimeRange(
        start_dt.replace(hour=start_time.hour,
                         minute=start_time.minute,
                         second=start_time.second),
        end_dt.replace(hour=end_time.hour,
                       minute=end_time.minute,
                       second=end_time.second)
    )
