from pydantic import BaseModel

from ...utils.responses.main import get_text


class UserResponsePatchSchema(BaseModel):
    message: str = get_text('patch').format('user', 1)


class UserResponseDeleteSchema(BaseModel):
    message: str = get_text('delete').format('user', 1)


class UserResponsePostSchema(BaseModel):
    message: str = get_text('post').format('user', 1)
