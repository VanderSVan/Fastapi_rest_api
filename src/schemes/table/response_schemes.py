from pydantic import BaseModel

from src.utils.responses.main import get_text


class TableResponsePatchSchema(BaseModel):
    message: str = get_text('patch').format('table', 1)


class TableResponseDeleteSchema(BaseModel):
    message: str = get_text('delete').format('table', 1)


class TableResponsePostSchema(BaseModel):
    message: str = get_text('post').format('table', 1)
