from dataclasses import dataclass
from datetime import time
from typing import NoReturn

from fastapi import status

from src.utils.exceptions import JSONException
from src.utils.response_generation.main import get_text


@dataclass
class SchedulePostOrPatchValidator:
    """Schedule validator clas for patch operations"""
    order_data: dict

    def validate_data(self) -> dict:
        """Main validator"""
        open_time: time = self.order_data.get('open_time')
        close_time: time = self.order_data.get('close_time')
        break_start_time: time = self.order_data.get('break_start_time')
        break_end_time: time = self.order_data.get('break_end_time')

        if self.check_existing_time(open_time, close_time):
            self.check_open_close_time(open_time, close_time)

        if self.check_existing_time(break_start_time, break_end_time):
            self.check_break_time(break_start_time, break_end_time)

        return self.order_data

    @staticmethod
    def check_existing_time(first_time: time, second_time: time) -> bool:
        if first_time and second_time:
            return True
        return False

    @staticmethod
    def check_open_close_time(open_time: time, close_time: time) -> NoReturn:
        """Base validator for open and close values"""

        if close_time == open_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_open_equal_close'))

        if close_time < open_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_close_less_open'))

    @staticmethod
    def check_break_time(break_start_time: time, break_end_time: time) -> NoReturn:
        """Base validator for break_start_time and break_end_time values"""

        if break_start_time == break_end_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_break_equal'))

        if break_end_time < break_start_time:
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message=get_text('schedule_err_break_end_less_start'))
