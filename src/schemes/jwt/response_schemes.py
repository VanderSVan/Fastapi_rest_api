from pydantic import BaseModel as BaseScheme


class Token(BaseScheme):
    access_token: str
    token_type: str
