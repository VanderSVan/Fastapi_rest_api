from pydantic import BaseModel

from ...utils.responses.main import get_text


class OrderResponsePutSchema(BaseModel):
    message: str = get_text('put').format('order', 1)


class OrderResponseDeleteSchema(BaseModel):
    message: str = get_text('delete').format('order', 1)


class OrderResponsePostSchema(BaseModel):
    message: str = get_text('post').format('order', 1)
