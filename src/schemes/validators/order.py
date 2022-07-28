from dataclasses import dataclass
from datetime import datetime as dt, timedelta as td
from math import ceil
from typing import NoReturn

from fastapi import status
from datetimerange import DateTimeRange

from ...utils.exceptions import JSONException
from ...models.table import TableModel
from ...models.schedule import ScheduleModel
from .utils import (find_daily_schedule,
                    convert_time_range_to_datetime_range,
                    _get_table_objects)


@dataclass
class OrderBaseValidator:
    """Base order validator class, that runs before validator schema"""
    order_data: dict

    def validate_data(self) -> dict:
        """Main validator."""
        self._validate_datetime_format()
        return self.order_data

    def _validate_datetime_format(self) -> NoReturn:
        """
        Datetime format validator.
        Checks datetime formats for compliance available formats.
        """
        start: str | dt = self.order_data.get('start_datetime')
        end: str | dt = self.order_data.get('end_datetime')
        available_formats = ['%Y-%m-%dT%H:%M', "%Y-%m-%d"]

        if start and end:
            for dt_format in available_formats:
                if self._convert_start_end_to_dt_format(start, end, dt_format):
                    return True

            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="Unsupported datetime format, should be '%Y-%m-%dT%H:%M' "
                                        "for 'get', 'put' or 'post' operations or "
                                        "'%Y-%m-%d' for 'get' operation only")

    @staticmethod
    def _convert_start_end_to_dt_format(start: str | dt,
                                        end: str | dt,
                                        dt_format: str) -> tuple[dt, dt] | None:
        """
        Converts 'start' and 'end' strings to datetime object.
        But if it gets an error doesn't raises exception, just return None.
        """
        if isinstance(start, str) and isinstance(end, str):
            try:
                start = dt.strptime(start, dt_format)
                end = dt.strptime(end, dt_format)
            finally:
                return (start, end) if isinstance(start, dt) and isinstance(end, dt) else None

        elif isinstance(start, dt) and isinstance(end, dt):
            processed_start = None
            processed_end = None
            try:
                processed_start = start.strftime(dt_format)
                processed_end = end.strftime(dt_format)
            finally:
                return (processed_start, processed_end) if processed_start and processed_end else None

        else:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="'start_datetime' and 'end_datetime' should be datetime string")


@dataclass
class OrderPatchValidator:
    """Order post request validator class."""
    order_data: dict

    def validate_data(self) -> dict:
        """Main validator"""
        self._check_datetime_values()
        self._check_available_time_in_schedule()
        self._transform_ids_into_table_objs()
        return self.order_data

    def _check_datetime_values(self) -> NoReturn:
        """Base validator for start and end values"""
        start: dt = self.order_data.get('start_datetime')
        end: dt = self.order_data.get('end_datetime')

        if end == start:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="fields 'start_datetime' and 'end_datetime' cannot be equal")

        if end < start:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="'end' time cannot be less than 'start' time")

        if start.date() != end.date():
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="'start' and 'end' datetime must have the same day")

    def _check_available_time_in_schedule(self) -> bool:
        """
        Returns True if the time is within the range of the daily schedule
        else raises JSONException
        """
        # get input data
        start: dt = self.order_data.get('start_datetime')
        end: dt = self.order_data.get('end_datetime')

        # get daily schedule by date or week day
        daily_schedule: ScheduleModel = find_daily_schedule(start.date())

        # convert time schedule range to datetime schedule range
        daily_schedule_without_break = convert_time_range_to_datetime_range(daily_schedule.open_time,
                                                                            daily_schedule.close_time,
                                                                            start,
                                                                            end)

        # convert break time to break datetime
        break_schedule = convert_time_range_to_datetime_range(daily_schedule.break_start_time,
                                                              daily_schedule.break_end_time,
                                                              start,
                                                              end)
        input_time_range = DateTimeRange(start, end)

        # check time ranges
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

    def _transform_ids_into_table_objs(self) -> list:
        """Converts integers to TableModel objects for nested model."""
        table_ids = self.order_data.get('tables')
        if table_ids:
            tables: list[TableModel] = _get_table_objects(table_ids)
            self.order_data['tables'] = tables
        else:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="Field 'tables' cannot be empty")
        return tables


@dataclass
class OrderPostValidator(OrderPatchValidator):
    """Order post request validator class."""
    order_data: dict

    def validate_data(self) -> dict:
        """Main validator"""
        self._check_datetime_values()
        self._check_available_time_in_schedule()
        tables: list[TableModel] = self._transform_ids_into_table_objs()
        hours: int = self._round_timedelta_to_hours()
        self._calculate_cost(hours, tables)
        return self.order_data

    def _round_timedelta_to_hours(self) -> int:
        """
        Round time delta to hours.
        Cuts off seconds and milliseconds.
        """
        start: dt = self.order_data.get('start_datetime')
        end: dt = self.order_data.get('end_datetime')
        dt_delta: td = end - start
        accurate_time_in_seconds = dt_delta.seconds / 3600
        return ceil(accurate_time_in_seconds)

    def _calculate_cost(self, hours, tables) -> NoReturn:
        """Calculates order cost by table.price_per_hour"""
        table_prices_per_hour: list = [table.price_per_hour for table in tables]
        total_price: float = sum(table_prices_per_hour)
        self.order_data['cost']: float = hours * total_price
