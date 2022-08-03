from dataclasses import dataclass
from datetime import datetime as dt
from typing import NoReturn

from fastapi import status

from ...utils.exceptions import JSONException


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
class OrderPostOrPatchValidator:
    """Order post request validator class."""
    order_data: dict

    def validate_data(self) -> dict:
        """Main validator"""
        self._check_datetime_values()
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
