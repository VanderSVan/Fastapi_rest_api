from dataclasses import dataclass
from datetime import datetime as dt
from typing import NoReturn

from fastapi import status

from src.utils.exceptions import JSONException
from src.utils.responses.main import get_text


@dataclass
class SchedulePatchValidator:
    """Schedule validator clas for patch operations"""
    order_data: dict

    def validate_data(self) -> dict:
        """Main validator"""
        open_time: dt = self.order_data.get('open_time')
        close_time: dt = self.order_data.get('close_time')
        break_start_time: dt = self.order_data.get('break_start_time')
        break_end_time: dt = self.order_data.get('break_end_time')

        if self._check_existing_time(open_time, close_time):
            self._check_open_close_time(open_time, close_time)

        if self._check_existing_time(break_start_time, break_end_time):
            self._check_break_time(break_start_time, break_end_time)

        return self.order_data

    @staticmethod
    def _check_existing_time(first_time: dt, second_time: dt) -> bool:
        if first_time and second_time:
            return True
        return False

    @staticmethod
    def _check_open_close_time(open_time: dt, close_time: dt) -> NoReturn:
        """Base validator for open and close values"""

        if close_time == open_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_open_equal_close'))

        if close_time < open_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_close_less_open'))

    @staticmethod
    def _check_break_time(break_start_time: dt, break_end_time: dt) -> NoReturn:
        """Base validator for break_start_time and break_end_time values"""

        if break_start_time == break_end_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_break_equal'))

        if break_end_time < break_start_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_break_end_less_start'))


@dataclass
class SchedulePostValidator(SchedulePatchValidator):
    """Schedule validator clas for post operations"""
    order_data: dict

    def validate_data(self) -> dict:
        """Main validator"""
        open_time: dt = self.order_data.get('open_time')
        close_time: dt = self.order_data.get('close_time')
        break_start_time: dt = self.order_data.get('break_start_time')
        break_end_time: dt = self.order_data.get('break_end_time')

        self._check_open_close_time(open_time, close_time)

        if self._check_existing_time(break_start_time, break_end_time):
            self._check_break_time(break_start_time, break_end_time)

        return self.order_data

    @staticmethod
    def _check_open_close_time(open_time: dt, close_time: dt) -> NoReturn:
        """Base validator for open and close values"""

        if not (close_time and open_time):
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_required'))

        if close_time == open_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_open_equal_close'))

        if close_time < open_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_close_less_open'))
