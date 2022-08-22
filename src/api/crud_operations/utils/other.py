from datetime import date, datetime as dt, timedelta as td
from math import ceil


def process_end_datetime(end: dt):
    """
    If date:
        Replaces empty time values to '23:59:59'.
        For proper search operation.
    else:
        Do nothing.
    :param end: date or datetime value.
    :return: datetime obj.
    """
    return (
        dt(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59)
        if type(end) is date else end
    )


def round_timedelta_to_hours(start: dt, end: dt) -> int:
    """
    Rounds time delta to hours.
    Cuts off seconds and milliseconds.
    """
    dt_delta: td = end - start
    accurate_time_in_seconds: float = dt_delta.seconds / 3600
    return ceil(accurate_time_in_seconds)