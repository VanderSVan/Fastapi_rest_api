from pydantic import BaseModel

from ...utils.responses.main import get_text


class ScheduleResponsePutSchema(BaseModel):
    message: str = get_text('put').format('schedule', 1)


class ScheduleResponseDeleteSchema(BaseModel):
    message: str = get_text('delete').format('schedule', 1)


class ScheduleResponsePostSchema(BaseModel):
    message: str = get_text('post').format('schedule', 1)
