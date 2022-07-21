from pydantic import BaseModel

from ...utils.responses.main import get_text


class TableResponsePutSchema(BaseModel):
    message: str = get_text('put').format('table', 1)


class TableResponseDeleteSchema(BaseModel):
    message: str = get_text('delete').format('table', 1)


class TableResponsePostSchema(BaseModel):
    message: str = get_text('post').format('table', 1)
