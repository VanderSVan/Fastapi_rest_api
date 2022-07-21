from sqlalchemy import Column, Integer, String, Time

from ..db.db_sqlalchemy import BaseModel


class ScheduleModel(BaseModel):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True)
    day = Column(String(length=25), unique=True)
    open_time = Column(Time)
    close_time = Column(Time)
    break_start_time = Column(Time, default=None, nullable=True)
    break_end_time = Column(Time, default=None, nullable=True)
