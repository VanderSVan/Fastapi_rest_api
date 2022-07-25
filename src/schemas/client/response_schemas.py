from pydantic import BaseModel

from ...utils.responses.main import get_text


class ClientResponsePatchSchema(BaseModel):
    message: str = get_text('patch').format('client', 1)


class ClientResponseDeleteSchema(BaseModel):
    message: str = get_text('delete').format('client', 1)


class ClientResponsePostSchema(BaseModel):
    message: str = get_text('post').format('client', 1)
