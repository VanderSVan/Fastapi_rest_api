from dataclasses import dataclass
from datetime import time, datetime as dt
from typing import NoReturn

from fastapi import status

from src.utils.exceptions import JSONException
from src.utils.responses.main import get_text


@dataclass
class ScheduleValidator:
    """Schedule validator clas for post and patch operations"""
    order_data: dict

    def validate_data(self) -> dict:
        """Main validator"""
        self._check_open_close_time()
        self._check_break_time()
        return self.order_data

    def _check_open_close_time(self) -> NoReturn:
        """Base validator for open and close values"""
        open_time: dt = self.order_data.get('open_time')
        close_time: dt = self.order_data.get('close_time')

        if not(close_time and open_time):
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_required'))

        if close_time == open_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_open_equal_close'))

        if close_time < open_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_close_less_open'))

    def _check_break_time(self) -> NoReturn:
        """Base validator for break_start_time and break_end_time values"""
        break_start_time: dt = self.order_data.get('break_start_time')
        break_end_time: dt = self.order_data.get('break_end_time')

        if not (break_start_time and break_end_time):
            self.order_data['break_start_time'] = None
            self.order_data['break_end_time'] = None
            return self.order_data

        if break_start_time == break_end_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_break_equal'))

        if break_end_time < break_start_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_break_end_less_start'))
