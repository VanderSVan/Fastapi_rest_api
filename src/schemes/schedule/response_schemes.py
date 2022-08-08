from pydantic import BaseModel

from src.utils.responses.main import get_text


class ScheduleResponsePatchSchema(BaseModel):
    message: str = get_text('patch').format('schedule', 1)


class ScheduleResponseDeleteSchema(BaseModel):
    message: str = get_text('delete').format('schedule', 1)


class ScheduleResponsePostSchema(BaseModel):
    message: str = get_text('post').format('schedule', 1)
