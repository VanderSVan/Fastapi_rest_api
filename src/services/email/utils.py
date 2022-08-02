import pytz
from datetime import datetime as dt
from datetime import timedelta as td

from src.config import Settings


def create_expire(expire: int = Settings.URL_EXPIRE_HOURS) -> str:
    """
    Creates an expiry time for the link.
    24 hours by default.
    :return: datetime as string
    """

    time_zone = pytz.timezone(Settings.TIME_ZONE)
    now = time_zone.localize(dt.now())
    expire = (
            now + td(hours=int(expire) or 24)
    ).strftime('%Y-%m-%d %H:%M:%S')

    return expire
