from pydantic import BaseModel

from ...utils.responses.main import get_text


class ClientResponsePutSchema(BaseModel):
    message: str = get_text('put').format('client', 1)


class ClientResponseDeleteSchema(BaseModel):
    message: str = get_text('delete').format('client', 1)


class ClientResponsePostSchema(BaseModel):
    message: str = get_text('post').format('client', 1)
